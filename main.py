from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path


YDOTOOLD = shutil.which("ydotoold")

SOCKET = Path(
    os.environ.get(
        "YDOTOOL_SOCKET",
        f"/run/user/{os.getuid()}/ydotool_socket",
    )
)

CHILD_ENV = "SOLSRNGCORE_GUI_CHILD"


def _daemon_running() -> bool:
    try:
        result = subprocess.run(
            [
                "pgrep",
                "-u",
                str(os.getuid()),
                "-x",
                "ydotoold",
            ],
            text=True,
            capture_output=True,
            check=False,
            timeout=2.0,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False

    return result.returncode == 0


def _socket_ready() -> bool:
    return SOCKET.exists()


def ensure_ydotoold() -> None:
    """Start ydotoold when necessary and configure its socket."""

    if YDOTOOLD is None:
        raise RuntimeError(
            "ydotoold is not installed or not in PATH."
        )

    os.environ["YDOTOOL_SOCKET"] = str(SOCKET)

    if _daemon_running() and _socket_ready():
        return

    if SOCKET.exists() and not _daemon_running():
        try:
            SOCKET.unlink()
        except OSError as exc:
            raise RuntimeError(
                f"Unable to remove stale ydotool socket: {exc}"
            ) from exc

    try:
        subprocess.Popen(
            [
                YDOTOOLD,
                "--socket-path",
                str(SOCKET),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as exc:
        raise RuntimeError(
            f"Failed to start ydotoold: {exc}"
        ) from exc

    for _ in range(30):
        if _daemon_running() and _socket_ready():
            return

        time.sleep(0.1)

    raise RuntimeError(
        f"ydotoold did not become ready at {SOCKET}"
    )


def _first_fatal_webhook() -> str:
    """
    Find the first enabled configured webhook.

    This is only used AFTER the GUI process has died, so it does
    not depend on the GUI event loop still being alive.
    """

    try:
        from solsrng_core.config import load_config

        config = load_config()

        for profile in config.profiles:
            if (
                profile.enabled
                and profile.url.strip()
            ):
                return profile.url.strip()

    except Exception as exc:
        print(
            f"[FATAL REPORT] Unable to load webhook config: {exc}",
            file=sys.stderr,
        )

    return ""


def _send_fatal_report(reason: str) -> None:
    """
    Send one bounded fatal report after the GUI process exits
    unexpectedly.
    """

    try:
        from solsrng_core.diagnostics.crash import send_fatal_report

        webhook_url = _first_fatal_webhook()

        if not webhook_url:
            print(
                "[FATAL REPORT] No enabled webhook configured.",
                file=sys.stderr,
            )
            return

        ok = send_fatal_report(
            webhook_url,
            reason,
        )

        if ok:
            print(
                "[FATAL REPORT] Fatal report sent.",
                file=sys.stderr,
            )
        else:
            print(
                "[FATAL REPORT] Failed to send fatal report.",
                file=sys.stderr,
            )

    except Exception as exc:
        # Crash reporting must NEVER cause another crash.
        print(
            f"[FATAL REPORT] {exc}",
            file=sys.stderr,
        )


def _run_gui_directly() -> int:
    """
    Run the actual GUI.

    The child process is marked with SOLSRNGCORE_GUI_CHILD so
    main.py does not recursively create supervisors.
    """

    from solsrng_core.gui.app import run

    ensure_ydotoold()

    return int(run())


def _run_supervised() -> int:
    """
    Start a child GUI process and watch its exit status.

    Normal:
        child exits 0 -> return 0

    Python/application crash:
        child exits non-zero -> send fatal report

    Native crash:
        child exits due to SIGSEGV/SIGABRT/etc -> send fatal report
    """

    env = os.environ.copy()
    env[CHILD_ENV] = "1"

    child = subprocess.Popen(
        [
            sys.executable,
            str(Path(__file__).resolve()),
        ],
        env=env,
    )

    try:
        code = child.wait()
    except KeyboardInterrupt:
        try:
            child.terminate()
        except OSError:
            pass

        try:
            child.wait(timeout=3.0)
        except subprocess.TimeoutExpired:
            try:
                child.kill()
            except OSError:
                pass

        return 130

    # Normal shutdown.
    if code == 0:
        return 0

    # Negative return code means a signal terminated the child.
    if code < 0:
        signal_number = -code

        try:
            signal_name = signal.Signals(
                signal_number
            ).name
        except ValueError:
            signal_name = f"SIG{signal_number}"

        reason = (
            "GUI terminated by native signal "
            f"{signal_name} ({signal_number})"
        )

    else:
        reason = (
            "GUI exited unexpectedly with code "
            f"{code}"
        )

    print(
        f"[FATAL] {reason}",
        file=sys.stderr,
    )

    _send_fatal_report(reason)

    return code


def main() -> int:
    # Child mode: run GUI normally.
    if os.environ.get(CHILD_ENV) == "1":
        return _run_gui_directly()

    # Parent mode: supervise GUI.
    return _run_supervised()


if __name__ == "__main__":
    raise SystemExit(main())

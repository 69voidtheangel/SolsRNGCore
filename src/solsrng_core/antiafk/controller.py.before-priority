from __future__ import annotations

import os
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Callable


class WindowError(RuntimeError):
    """Raised when Anti-AFK cannot perform an input action."""


class AntiAFKController:
    """
    Cross-platform Linux Anti-AFK controller.

    Supported methods:
        space
            Wait for the configured interval, then press Space.

        alt_tab
            Alt+Tab to the next window, press Space, then Alt+Tab back.

    Supported backends:
        auto
        ydotool
        xdotool
    """

    SPACE_MODE = "space"
    ALT_TAB_MODE = "alt_tab"

    def __init__(
        self,
        interval_seconds: float = 120.0,
        method: str = SPACE_MODE,
        backend_preference: str = "auto",
        log: Callable[[str], None] | None = None,
        priority_gate=None,
    ):
        self.interval_seconds = max(
            1.0,
            float(interval_seconds),
        )

        self.method = self._normalize_method(
            method
        )

        if self._environment_is_kde_wayland():
            self.method = self.SPACE_MODE

        self.backend_preference = (
            self._normalize_backend(
                backend_preference
            )
        )

        self.log = log or (
            lambda _: None
        )

        self.priority_gate = priority_gate

        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    # ---------------------------------------------------------
    # Environment
    # ---------------------------------------------------------

    @staticmethod
    def _environment_is_kde_wayland() -> bool:
        session = __import__("os").environ.get(
            "XDG_SESSION_TYPE",
            "",
        ).strip().lower()

        desktop = __import__("os").environ.get(
            "XDG_CURRENT_DESKTOP",
            "",
        ).strip().lower()

        return (
            session == "wayland"
            and "kde" in desktop
        )

    # ---------------------------------------------------------
    # Normalization
    # ---------------------------------------------------------

    @classmethod
    def _normalize_method(
        cls,
        method: str,
    ) -> str:
        value = (
            str(method)
            .strip()
            .lower()
        )

        aliases = {
            "space": cls.SPACE_MODE,
            "space mode": cls.SPACE_MODE,
            "alt+tab": cls.ALT_TAB_MODE,
            "alt-tab": cls.ALT_TAB_MODE,
            "alt tab": cls.ALT_TAB_MODE,
            "alt_tab": cls.ALT_TAB_MODE,
        }

        normalized = aliases.get(value)

        if normalized is None:
            raise WindowError(
                f"Unsupported Anti-AFK method: {method}"
            )

        return normalized

    @staticmethod
    def _normalize_backend(
        backend: str,
    ) -> str:
        value = (
            str(backend)
            .strip()
            .lower()
        )

        if value not in {
            "auto",
            "ydotool",
            "xdotool",
        }:
            raise WindowError(
                f"Unsupported input backend: {backend}"
            )

        return value

    # ---------------------------------------------------------
    # State
    # ---------------------------------------------------------

    @property
    def running(self) -> bool:
        return (
            self._thread is not None
            and self._thread.is_alive()
        )

    # ---------------------------------------------------------
    # Backend selection
    # ---------------------------------------------------------

    def _is_kde_wayland(self) -> bool:
        session = os.environ.get(
            "XDG_SESSION_TYPE",
            "",
        ).strip().lower()

        desktop = os.environ.get(
            "XDG_CURRENT_DESKTOP",
            "",
        ).strip().lower()

        return (
            session == "wayland"
            and "kde" in desktop
            and shutil.which("wdotool") is not None
        )

    def _backend(self) -> str:
        requested = self.backend_preference

        # KDE Wayland: prefer the compositor-aware wdotool KDE backend.
        if self._is_kde_wayland():
            if requested == "xdotool":
                if shutil.which("xdotool") is None:
                    raise WindowError(
                        "xdotool is not installed or not in PATH"
                    )

                return "xdotool"

            if shutil.which("wdotool") is None:
                raise WindowError(
                    "wdotool is required for KDE Wayland Anti-AFK."
                )

            return "wdotool"

        if requested == "ydotool":
            if shutil.which("ydotool") is None:
                raise WindowError(
                    "ydotool is not installed or not in PATH"
                )

            return "ydotool"

        if requested == "xdotool":
            if shutil.which("xdotool") is None:
                raise WindowError(
                    "xdotool is not installed or not in PATH"
                )

            return "xdotool"

        if shutil.which("ydotool") is not None:
            return "ydotool"

        if shutil.which("xdotool") is not None:
            return "xdotool"

        raise WindowError(
            "No supported input backend was found. "
            "Install ydotool or xdotool."
        )

    def _wdotool(self, *args: str) -> subprocess.CompletedProcess[str]:
        if shutil.which("wdotool") is None:
            raise WindowError(
                "wdotool is not installed or not in PATH"
            )

        try:
            return subprocess.run(
                [
                    "wdotool",
                    "--backend",
                    "kde",
                    *args,
                ],
                text=True,
                capture_output=True,
                check=False,
                timeout=10.0,
            )
        except subprocess.TimeoutExpired:
            raise WindowError(
                "wdotool timed out"
            )
        except OSError as exc:
            raise WindowError(
                f"Unable to execute wdotool: {exc}"
            )

    def _active_window(self) -> tuple[str, str]:
        result = self._wdotool(
            "getactivewindow",
        )

        if result.returncode != 0:
            raise WindowError(
                result.stderr.strip()
                or "wdotool could not determine the active window"
            )

        window_id = result.stdout.strip()

        if not window_id:
            raise WindowError(
                "wdotool returned an empty active window ID"
            )

        title_result = self._wdotool(
            "getwindowname",
            window_id,
        )

        title = (
            title_result.stdout.strip()
            if title_result.returncode == 0
            else ""
        )

        return window_id, title

    def _find_sober(self) -> tuple[str, str]:
        patterns = (
            "Sober",
            "Roblox",
        )

        for pattern in patterns:
            result = self._wdotool(
                "search",
                "--name",
                pattern,
                "--ignore-case",
            )

            if result.returncode != 0:
                continue

            for line in result.stdout.splitlines():
                line = line.strip()

                if not line:
                    continue

                window_id = line.split(None, 1)[0]

                title_result = self._wdotool(
                    "getwindowname",
                    window_id,
                )

                if title_result.returncode != 0:
                    continue

                title = title_result.stdout.strip()

                if (
                    pattern.lower() == "sober"
                    and title.lower() == "sober"
                ):
                    return window_id, title

                if (
                    pattern.lower() == "roblox"
                    and "roblox" in title.lower()
                ):
                    return window_id, title

        raise WindowError(
            "Could not find the Sober game window."
        )

    def _activate_window(self, window_id: str, title: str) -> None:
        # The KDE backend may expose transient IDs. Re-resolve by title
        # immediately before activation when possible.
        search = self._wdotool(
            "search",
            "--name",
            title,
            "--ignore-case",
        )

        resolved_id = window_id

        if search.returncode == 0:
            for line in search.stdout.splitlines():
                line = line.strip()

                if not line:
                    continue

                candidate = line.split(None, 1)[0]

                candidate_title = self._wdotool(
                    "getwindowname",
                    candidate,
                )

                if (
                    candidate_title.returncode == 0
                    and candidate_title.stdout.strip() == title
                ):
                    resolved_id = candidate
                    break

        result = self._wdotool(
            "windowactivate",
            resolved_id,
        )

        if result.returncode != 0:
            raise WindowError(
                result.stderr.strip()
                or result.stdout.strip()
                or f'Could not focus "{title}"'
            )

        time.sleep(0.35)

        active_id, active_title = self._active_window()

        if active_title != title:
            raise WindowError(
                f'Window activation was not confirmed for "{title}". '
                f'Active window is "{active_title}".'
            )

    def _run_sober_tick(self) -> None:
        previous_id, previous_title = self._active_window()

        self.log(
            f'Anti-AFK: remembered "{previous_title}"'
        )

        sober_id, sober_title = self._find_sober()

        self.log(
            f'Anti-AFK: focusing "{sober_title}"'
        )

        try:
            # Focus the actual Sober window.
            self._activate_window(
                sober_id,
                sober_title,
            )

            # Give Roblox/Sober a moment to settle after focus changes.
            time.sleep(0.5)

            # Send the proven working Space input through the
            # SolsRNGCore-owned ydotool socket.
            self._press_space()

            self.log(
                "Anti-AFK: Space pressed in Sober"
            )

        finally:
            # Always return to the window that was active before
            # the Anti-AFK cycle began.
            time.sleep(0.20)

            try:
                self._activate_window(
                    previous_id,
                    previous_title,
                )

                self.log(
                    f'Anti-AFK: restored "{previous_title}"'
                )

            except WindowError as exc:
                self.log(
                    "Anti-AFK: previous-window restore failed: "
                    f"{exc}"
                )
                raise

    # ---------------------------------------------------------
    # Input
    # ---------------------------------------------------------

    @staticmethod
    def _keycode(
        key: str,
    ) -> int:
        keycodes = {
            "tab": 15,
            "space": 57,
            "alt": 56,
        }

        normalized = (
            str(key)
            .strip()
            .lower()
        )

        if normalized not in keycodes:
            raise WindowError(
                f"Unsupported Anti-AFK key: {key}"
            )

        return keycodes[normalized]

    def _run(
        self,
        *args: str,
        timeout: float = 5.0,
    ) -> None:
        backend = self._backend()

        if backend == "wdotool":
            command = [
                "wdotool",
                "--backend",
                "kde",
                *args,
            ]

        elif backend == "ydotool":
            command = [
                "ydotool",
                *args,
            ]

        else:
            command = [
                "xdotool",
                *args,
            ]

        environment = os.environ.copy()

        try:
            result = subprocess.run(
                command,
                text=True,
                capture_output=True,
                check=False,
                timeout=timeout,
                env=environment,
            )
        except subprocess.TimeoutExpired:
            raise WindowError(
                f"{backend} timed out while sending input"
            )
        except OSError as exc:
            raise WindowError(
                f"Unable to execute {backend}: {exc}"
            )

        if result.returncode != 0:
            error = (
                result.stderr.strip()
                or result.stdout.strip()
                or f"unknown {backend} error"
            )

            raise WindowError(error)

    def _press_space(
        self,
    ) -> None:
        backend = self._backend()

        if backend == "wdotool":
            # KDE Wayland should never use wdotool for keyboard injection.
            # Fall through to the ydotool-backed keyboard path.
            backend = "ydotool"

        if backend == "ydotool":
            code = self._keycode("space")

            socket_path = (
                f"/run/user/{os.getuid()}/"
                ".solsrng_ydotool_socket"
            )

            if not Path(socket_path).exists():
                raise WindowError(
                    f"SolsRNGCore ydotool socket is missing: {socket_path}"
                )

            environment = os.environ.copy()
            environment["YDOTOOL_SOCKET"] = socket_path

            try:
                subprocess.run(
                    [
                        "ydotool",
                        "key",
                        f"{code}:1",
                    ],
                    text=True,
                    capture_output=True,
                    check=True,
                    timeout=5.0,
                    env=environment,
                )

                time.sleep(0.5)

                subprocess.run(
                    [
                        "ydotool",
                        "key",
                        f"{code}:0",
                    ],
                    text=True,
                    capture_output=True,
                    check=True,
                    timeout=5.0,
                    env=environment,
                )

            except subprocess.CalledProcessError as exc:
                detail = (
                    exc.stderr.strip()
                    if exc.stderr
                    else str(exc)
                )
                raise WindowError(
                    f"ydotool Space input failed: {detail}"
                )

            return

        self._run(
            "keydown",
            "space",
        )

        time.sleep(0.5)

        self._run(
            "keyup",
            "space",
        )

    def _alt_tab_once(
        self,
    ) -> None:
        backend = self._backend()

        if backend == "ydotool":
            alt = self._keycode("alt")
            tab = self._keycode("tab")

            self._run(
                "key",
                f"{alt}:1",
                f"{tab}:1",
                f"{tab}:0",
                f"{alt}:0",
            )
            return

        self._run(
            "key",
            "alt+Tab",
        )

    # ---------------------------------------------------------
    # Modes
    # ---------------------------------------------------------

    def _run_space_mode(
        self,
    ) -> None:
        if self._is_kde_wayland():
            self._run_sober_tick()
            return

        self._press_space()

        self.log(
            "Anti-AFK: Space pressed"
        )

    def _run_alt_tab_mode(
        self,
    ) -> None:
        if self._is_kde_wayland():
            self._run_sober_tick()
            return

        self._alt_tab_once()
        time.sleep(0.20)

        try:
            self._press_space()

            self.log(
                "Anti-AFK: Alt+Tab → Space"
            )

        finally:
            time.sleep(0.20)

            try:
                self._alt_tab_once()
            except WindowError as exc:
                self.log(
                    "Anti-AFK: failed to Alt+Tab back: "
                    f"{exc}"
                )
                raise

        self.log(
            "Anti-AFK: returned to previous window"
        )

    def _tick(self) -> None:
        if self._is_kde_wayland():
            self._run_sober_tick()
            return

        if self.method == self.SPACE_MODE:
            self._run_space_mode()

        elif self.method == self.ALT_TAB_MODE:
            self._run_alt_tab_mode()

        else:
            raise WindowError(
                f"Unsupported Anti-AFK method: {self.method}"
            )

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def start(self) -> None:
        if self.running:
            return

        self._stop.clear()

        # Validate the configured backend only.
        self._backend()

        self._thread = threading.Thread(
            target=self._loop,
            name="SolsRNG-AntiAFK",
            daemon=True,
        )

        self._thread.start()

        self.log(
            f"Anti-AFK started "
            f"(method={self.method}, backend={self._backend()})"
        )

    def stop(
        self,
        restore: bool = True,
    ) -> None:
        del restore

        self._stop.set()

        thread = self._thread

        if (
            thread is not None
            and thread is not threading.current_thread()
        ):
            thread.join(
                timeout=3.0
            )

            if thread.is_alive():
                self.log(
                    "Anti-AFK worker did not stop "
                    "within timeout"
                )

        self._thread = None

        self.log(
            "Anti-AFK stopped"
        )

    def _loop(self) -> None:
        # Run the first Anti-AFK cycle immediately after Start.
        # Subsequent cycles use the configured interval.
        while not self._stop.is_set():
            try:
                if self.priority_gate is not None:
                    self.priority_gate.enter_afk()

                try:
                    self._tick()
                finally:
                    if self.priority_gate is not None:
                        self.priority_gate.leave()

            except WindowError as exc:
                self.log(
                    f"Anti-AFK error: {exc}"
                )

            except Exception as exc:
                self.log(
                    f"Anti-AFK unexpected error: {exc}"
                )

    # ---------------------------------------------------------
    # Compatibility helpers
    # ---------------------------------------------------------

            if self._stop.wait(self.interval_seconds):
                break

    def swap_to_game(self) -> None:
        self.log(
            "Anti-AFK: focus switching is handled "
            "automatically by Alt+Tab mode"
        )

    def restore_previous_window(self) -> None:
        self.log(
            "Anti-AFK: previous-window restore is handled "
            "automatically by Alt+Tab mode"
        )

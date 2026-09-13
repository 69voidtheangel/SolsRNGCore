from __future__ import annotations

import os
import shutil
import signal
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .models import AutomationCoordinates, AutomationItem


class AutomationError(RuntimeError):
    pass


@dataclass
class WindowInfo:
    window_id: str
    title: str


@dataclass
class AutomationStatus:
    running: bool = False
    testing: bool = False
    message: str = "STOPPED"
    current_item: str = ""
    next_run_timestamp: float | None = None
    authenticated: bool = False
    authenticating: bool = False
    auth_error: str = ""
    game_window: str = ""
    previous_window: str = ""


class AutomationController:
    """
    Reliable Linux automation controller.

    KDE Wayland:
        - wdotool KDE backend for window discovery/focus/restore.
        - ydotool through the SolsRNGCore-owned socket for mouse/keyboard.
        - Window activation is re-resolved by exact title before use.
        - Focus is verified after activation.
        - Previous window restoration is retried and verified.

    X11/XWayland:
        - xdotool/window tools are retained as the legacy path.

    Public interface intentionally matches the existing Automation GUI.
    """

    RETRIES = 3
    COMMAND_TIMEOUT = 10.0
    FOCUS_DELAY = 0.35
    POST_FOCUS_DELAY = 0.50
    RESTORE_DELAY = 0.20
    CLICK_SETTLE = 0.15
    TYPE_SETTLE = 0.20

    def __init__(
        self,
        *,
        backend: str = "auto",
        game_window_pattern: str = "Sober",
        on_status: Callable[[AutomationStatus], None] | None = None,
        priority_gate=None,
    ):
        self.backend = (backend or "auto").strip().lower()
        self.game_window_pattern = (
            game_window_pattern or "Sober"
        ).strip()

        self.on_status = on_status
        self.priority_gate = priority_gate
        self.items: list[AutomationItem] = []

        # One coordinate set shared by every automation item.
        self.coordinates = AutomationCoordinates()

        self.status = AutomationStatus()

        self._thread: threading.Thread | None = None
        self._auth_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._run_lock = threading.Lock()

        self._socket_path: Path | None = None
        self._owned_ydotoold: subprocess.Popen | None = None

    # =========================================================
    # Environment
    # =========================================================

    @staticmethod
    def _is_kde_wayland() -> bool:
        desktop = os.environ.get(
            "XDG_CURRENT_DESKTOP",
            "",
        ).strip().lower()

        session = os.environ.get(
            "XDG_SESSION_TYPE",
            "",
        ).strip().lower()

        return (
            session == "wayland"
            and "kde" in desktop
        )

    # =========================================================
    # Status
    # =========================================================

    def _emit_status(self) -> None:
        callback = self.on_status

        if callback is None:
            return

        try:
            callback(self.status)
        except Exception:
            pass

    def _set_message(
        self,
        message: str,
        *,
        current_item: str | None = None,
    ) -> None:
        self.status.message = message

        if current_item is not None:
            self.status.current_item = current_item

        self._emit_status()

    # =========================================================
    # Authentication
    # =========================================================

    def authenticate_async(self):
        if self.status.authenticated:
            return

        if self.status.authenticating:
            return

        self.status.authenticating = True
        self.status.auth_error = ""
        self._emit_status()

        self._auth_thread = threading.Thread(
            target=self.authenticate,
            name="solsrng-automation-auth",
            daemon=True,
        )
        self._auth_thread.start()

    def authenticate(self) -> bool:
        try:
            backend = self._resolve_input_backend()

            if backend == "xdotool":
                self._socket_path = None
            else:
                self._ensure_ydotoold()

            self._verify_input_backend()

            self.status.authenticated = True
            self.status.auth_error = ""
            return True

        except Exception as exc:
            self.status.authenticated = False
            self.status.auth_error = str(exc)
            return False

        finally:
            self.status.authenticating = False
            self._emit_status()

    def retry_authentication(self):
        self.status.authenticated = False
        self.status.auth_error = ""
        self.authenticate_async()

    # =========================================================
    # Input backend
    # =========================================================

    def _resolve_input_backend(self) -> str:
        requested = self.backend or "auto"

        if self._is_kde_wayland():
            if requested == "xdotool":
                if shutil.which("xdotool") is None:
                    raise AutomationError(
                        "xdotool is not installed."
                    )
                return "xdotool"

            if shutil.which("ydotool") is None:
                raise AutomationError(
                    "ydotool is required for KDE Wayland automation."
                )

            return "ydotool"

        if requested == "ydotool":
            if shutil.which("ydotool") is None:
                raise AutomationError(
                    "ydotool is not installed."
                )
            return "ydotool"

        if requested == "xdotool":
            if shutil.which("xdotool") is None:
                raise AutomationError(
                    "xdotool is not installed."
                )
            return "xdotool"

        if requested == "auto":
            if shutil.which("ydotool") is not None:
                return "ydotool"

            if shutil.which("xdotool") is not None:
                return "xdotool"

            raise AutomationError(
                "No supported automation input backend was found."
            )

        raise AutomationError(
            f"Unknown automation backend: {requested}"
        )

    # Compatibility alias for any existing callers.
    def _resolve_backend(self) -> str:
        return self._resolve_input_backend()

    def _ensure_ydotoold(self) -> None:
        runtime = Path(
            os.environ.get(
                "XDG_RUNTIME_DIR",
                f"/run/user/{os.getuid()}",
            )
        )

        runtime.mkdir(
            parents=True,
            exist_ok=True,
        )

        socket_path = (
            runtime
            / ".solsrng_ydotool_socket"
        )

        self._socket_path = socket_path

        if socket_path.exists():
            return

        daemon = shutil.which("ydotoold")

        if daemon is None:
            raise AutomationError(
                "ydotoold is required for ydotool automation."
            )

        uid = os.getuid()
        gid = os.getgid()

        if shutil.which("pkexec"):
            command = [
                "pkexec",
                daemon,
                "--socket-path",
                str(socket_path),
                "--socket-perm",
                "0660",
                "--socket-own",
                f"{uid}:{gid}",
            ]
        else:
            command = [
                "sudo",
                "-n",
                "--",
                daemon,
                "--socket-path",
                str(socket_path),
                "--socket-perm",
                "0660",
                "--socket-own",
                f"{uid}:{gid}",
            ]

        self._owned_ydotoold = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        deadline = time.monotonic() + 5.0

        while time.monotonic() < deadline:
            if socket_path.exists():
                return

            if (
                self._owned_ydotoold.poll()
                is not None
            ):
                break

            time.sleep(0.10)

        raise AutomationError(
            "ydotoold could not be started."
        )

    def _verify_input_backend(self) -> None:
        backend = self._resolve_input_backend()

        if backend == "ydotool":
            if self._socket_path is None:
                self._ensure_ydotoold()

            if (
                self._socket_path is None
                or not self._socket_path.exists()
            ):
                raise AutomationError(
                    "SolsRNGCore ydotool socket is unavailable."
                )

    # =========================================================
    # Window command helpers
    # =========================================================

    def _run_command(
        self,
        command: list[str],
        *,
        timeout: float | None = None,
    ) -> subprocess.CompletedProcess[str]:
        timeout = (
            self.COMMAND_TIMEOUT
            if timeout is None
            else timeout
        )

        try:
            return subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
                env=os.environ.copy(),
            )
        except subprocess.TimeoutExpired:
            raise AutomationError(
                f"{command[0]} timed out."
            )
        except OSError as exc:
            raise AutomationError(
                f"Unable to execute {command[0]}: {exc}"
            )

    # Compatibility helper retained for GUI/tests.
    def _run_window_command(self, *args: str):
        if not args:
            raise AutomationError(
                "No window command specified."
            )

        if shutil.which(args[0]) is None:
            raise AutomationError(
                f"{args[0]} is not installed."
            )

        return self._run_command(list(args))

    # =========================================================
    # KDE Wayland window helpers
    # =========================================================

    def _wdotool(self, *args: str):
        if shutil.which("wdotool") is None:
            raise AutomationError(
                "wdotool is required for KDE Wayland window control."
            )

        return self._run_command(
            [
                "wdotool",
                "--backend",
                "kde",
                *args,
            ]
        )

    def _active_window_kde(self) -> WindowInfo:
        result = self._wdotool(
            "getactivewindow",
        )

        if result.returncode != 0:
            raise AutomationError(
                result.stderr.strip()
                or "wdotool could not determine the active window."
            )

        window_id = result.stdout.strip()

        if not window_id:
            raise AutomationError(
                "wdotool returned an empty active window ID."
            )

        title_result = self._wdotool(
            "getwindowname",
            window_id,
        )

        if title_result.returncode != 0:
            raise AutomationError(
                title_result.stderr.strip()
                or "Could not determine active window title."
            )

        return WindowInfo(
            window_id=window_id,
            title=title_result.stdout.strip(),
        )

    def _search_kde_windows(
        self,
        pattern: str,
    ) -> list[WindowInfo]:
        result = self._wdotool(
            "search",
            "--name",
            pattern,
            "--ignore-case",
        )

        if result.returncode != 0:
            return []

        windows: list[WindowInfo] = []

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

            if not title:
                continue

            windows.append(
                WindowInfo(
                    window_id=window_id,
                    title=title,
                )
            )

        return windows

    def _resolve_kde_window(
        self,
        window: WindowInfo,
    ) -> WindowInfo:
        exact = self._search_kde_windows(
            window.title,
        )

        for candidate in exact:
            if candidate.title == window.title:
                return candidate

        for candidate in exact:
            if (
                candidate.title.lower()
                == window.title.lower()
            ):
                return candidate

        raise AutomationError(
            f'Could not re-resolve window "{window.title}".'
        )

    def _activate_kde_window(
        self,
        window: WindowInfo,
    ) -> None:
        resolved = self._resolve_kde_window(
            window,
        )

        last_error = ""

        for _ in range(self.RETRIES):
            result = self._wdotool(
                "windowactivate",
                resolved.window_id,
            )

            if result.returncode != 0:
                last_error = (
                    result.stderr.strip()
                    or result.stdout.strip()
                    or "windowactivate failed"
                )
                time.sleep(0.20)

                try:
                    resolved = self._resolve_kde_window(
                        window,
                    )
                except AutomationError as exc:
                    last_error = str(exc)

                continue

            time.sleep(self.FOCUS_DELAY)

            try:
                active = self._active_window_kde()
            except AutomationError as exc:
                last_error = str(exc)
                time.sleep(0.20)
                continue

            if (
                active.title == resolved.title
                or active.title.lower()
                == resolved.title.lower()
            ):
                return

            last_error = (
                f'Active window is "{active.title}", '
                f'not "{resolved.title}".'
            )

            time.sleep(0.20)

            try:
                resolved = self._resolve_kde_window(
                    window,
                )
            except AutomationError as exc:
                last_error = str(exc)

        raise AutomationError(
            f'Could not focus window "{window.title}". '
            f"{last_error}"
        )

    # =========================================================
    # Legacy X11 window helpers
    # =========================================================

    def _list_windows_x11(self) -> list[WindowInfo]:
        windows: list[WindowInfo] = []

        if shutil.which("wmctrl"):
            result = self._run_window_command(
                "wmctrl",
                "-l",
            )

            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    parts = line.split(None, 3)

                    if len(parts) >= 4:
                        windows.append(
                            WindowInfo(
                                window_id=parts[0],
                                title=parts[3].strip(),
                            )
                        )

                if windows:
                    return windows

        if shutil.which("xdotool"):
            result = self._run_window_command(
                "xdotool",
                "search",
                "--name",
                ".*",
            )

            if result.returncode == 0:
                for raw_id in result.stdout.splitlines():
                    window_id = raw_id.strip()

                    if not window_id:
                        continue

                    title_result = self._run_window_command(
                        "xdotool",
                        "getwindowname",
                        window_id,
                    )

                    if title_result.returncode != 0:
                        continue

                    windows.append(
                        WindowInfo(
                            window_id=window_id,
                            title=title_result.stdout.strip(),
                        )
                    )

        if not windows:
            raise AutomationError(
                "Could not enumerate desktop windows. "
                "Install wmctrl or xdotool."
            )

        return windows

    # =========================================================
    # Window API
    # =========================================================

    def _get_active_window(self) -> WindowInfo:
        if self._is_kde_wayland():
            return self._active_window_kde()

        if shutil.which("xdotool"):
            result = self._run_window_command(
                "xdotool",
                "getactivewindow",
            )

            if result.returncode == 0:
                window_id = result.stdout.strip()

                if window_id:
                    title = (
                        self._run_window_command(
                            "xdotool",
                            "getwindowname",
                            window_id,
                        )
                        .stdout
                        .strip()
                    )

                    return WindowInfo(
                        window_id=window_id,
                        title=title,
                    )

        raise AutomationError(
            "Could not determine the active window."
        )

    def _list_windows(self) -> list[WindowInfo]:
        if self._is_kde_wayland():
            # A broad KDE search gives us enough candidates to
            # support exact and partial matching.
            candidates = self._search_kde_windows(".*")

            if candidates:
                return candidates

            # KDE's search implementation may not treat .* as
            # a universal query on every version, so fall back
            # to known useful names.
            combined: list[WindowInfo] = []

            seen: set[str] = set()

            for pattern in (
                "Sober",
                "Roblox",
                "Brave",
                "Discord",
                "Konsole",
                "Yakuake",
            ):
                for window in self._search_kde_windows(
                    pattern,
                ):
                    if window.window_id in seen:
                        continue

                    seen.add(window.window_id)
                    combined.append(window)

            if combined:
                return combined

            raise AutomationError(
                "Could not enumerate KDE Wayland windows."
            )

        return self._list_windows_x11()

    def find_game_window(self) -> WindowInfo:
        pattern = self.game_window_pattern.strip()

        if not pattern:
            raise AutomationError(
                "Game window search text is empty."
            )

        if self._is_kde_wayland():
            # Prefer an exact Sober match, then the configured
            # pattern, then Roblox.
            search_patterns = [
                "Sober",
            ]

            if pattern.lower() != "sober":
                search_patterns.append(pattern)

            search_patterns.append("Roblox")

            seen: set[str] = set()

            for search_pattern in search_patterns:
                for window in self._search_kde_windows(
                    search_pattern,
                ):
                    if window.window_id in seen:
                        continue

                    seen.add(window.window_id)

                    if (
                        search_pattern.lower() == "sober"
                        and window.title.lower()
                        == "sober"
                    ):
                        return window

                    if (
                        search_pattern.lower() == "roblox"
                        and "roblox"
                        in window.title.lower()
                    ):
                        return window

                    if (
                        search_pattern.lower()
                        not in {"sober", "roblox"}
                        and (
                            window.title.lower()
                            == search_pattern.lower()
                            or search_pattern.lower()
                            in window.title.lower()
                        )
                    ):
                        return window

            raise AutomationError(
                f'No game window matched "{pattern}".'
            )

        windows = self._list_windows()
        lowered = pattern.lower()

        exact = [
            window
            for window in windows
            if window.title.lower() == lowered
        ]

        if exact:
            return exact[0]

        partial = [
            window
            for window in windows
            if lowered in window.title.lower()
        ]

        if partial:
            return partial[0]

        sober = [
            window
            for window in windows
            if window.title.lower() == "sober"
        ]

        if sober:
            return sober[0]

        roblox = [
            window
            for window in windows
            if "roblox" in window.title.lower()
        ]

        if roblox:
            return roblox[0]

        raise AutomationError(
            f'No game window matched "{pattern}".'
        )

    def _activate_window(
        self,
        window: WindowInfo,
    ) -> None:
        if self._is_kde_wayland():
            self._activate_kde_window(
                window,
            )
            return

        if shutil.which("wmctrl"):
            result = self._run_window_command(
                "wmctrl",
                "-ia",
                window.window_id,
            )

            if result.returncode == 0:
                time.sleep(self.FOCUS_DELAY)
                return

        if shutil.which("xdotool"):
            result = self._run_window_command(
                "xdotool",
                "windowactivate",
                "--sync",
                window.window_id,
            )

            if result.returncode == 0:
                time.sleep(self.FOCUS_DELAY)
                return

        raise AutomationError(
            f'Could not focus window "{window.title}".'
        )

    def _restore_window(
        self,
        window: WindowInfo,
    ) -> None:
        last_error = ""

        for attempt in range(self.RETRIES):
            try:
                # Re-resolve by title every time on KDE Wayland.
                if self._is_kde_wayland():
                    self._activate_kde_window(
                        window,
                    )
                else:
                    self._activate_window(
                        window,
                    )

                active = self._get_active_window()

                if (
                    active.title.lower()
                    == window.title.lower()
                ):
                    return

                last_error = (
                    f'active window is "{active.title}"'
                )

            except Exception as exc:
                last_error = str(exc)

            if attempt < self.RETRIES - 1:
                time.sleep(
                    self.RESTORE_DELAY
                    * (attempt + 1)
                )

        raise AutomationError(
            f'Could not restore previous window '
            f'"{window.title}". {last_error}'
        )

    # =========================================================
    # Validation
    # =========================================================

    def _validate_item(
        self,
        item: AutomationItem,
    ):
        if not item.search_text.strip():
            raise AutomationError(
                f"{item.name}: search text is empty."
            )

        missing = item.coordinates.missing()

        if missing:
            raise AutomationError(
                f"{item.name}: missing coordinates: "
                + ", ".join(missing)
            )

        if item.cooldown_seconds < 0:
            raise AutomationError(
                f"{item.name}: cooldown cannot be negative."
            )

    def _validate_items(self):
        enabled = [
            item
            for item in self.items
            if item.enabled
        ]

        if not enabled:
            raise AutomationError(
                "No enabled automation items."
            )

        for item in enabled:
            self._validate_item(item)

    # =========================================================
    # Runtime
    # =========================================================

    def start(self):
        if self.status.running:
            return

        if not self.status.authenticated:
            raise AutomationError(
                "Input Access is not authenticated."
            )

        self._validate_items()

        self._verify_input_backend()

        self._stop_event.clear()

        self.status.running = True
        self.status.testing = False
        self.status.message = "RUNNING"
        self.status.current_item = ""
        self.status.next_run_timestamp = None
        self._emit_status()

        self._thread = threading.Thread(
            target=self._worker,
            name="solsrng-automation",
            daemon=True,
        )
        self._thread.start()

    def test_item(
        self,
        item: AutomationItem,
    ):
        if self.status.testing:
            return

        if self.status.running:
            raise AutomationError(
                "Stop Automation before running a test."
            )

        if not self.status.authenticated:
            raise AutomationError(
                "Input Access is not authenticated."
            )

        self._validate_item(item)
        self._verify_input_backend()

        if not self._run_lock.acquire(
            blocking=False
        ):
            raise AutomationError(
                "Automation is already busy."
            )

        self.status.testing = True
        self.status.message = (
            f"TESTING • {item.name}"
        )
        self.status.current_item = item.name
        self._emit_status()

        try:
            self._run_item(item)

            self.status.message = (
                f"TEST COMPLETE • {item.name}"
            )

        except Exception as exc:
            self.status.message = (
                f"TEST ERROR • {exc}"
            )
            raise

        finally:
            self.status.testing = False
            self.status.current_item = ""
            self._emit_status()
            self._run_lock.release()

    def stop(self):
        self._stop_event.set()

        self.status.running = False
        self.status.testing = False
        self.status.message = "STOPPED"
        self.status.current_item = ""
        self.status.next_run_timestamp = None

        self._emit_status()

    def shutdown(self):
        self.stop()

        daemon = self._owned_ydotoold

        if (
            daemon is not None
            and daemon.poll() is None
        ):
            try:
                daemon.send_signal(
                    signal.SIGTERM
                )
            except Exception:
                pass

        self._owned_ydotoold = None

    # =========================================================
    # Scheduler
    # =========================================================

    def _worker(self):
        enabled = [
            item
            for item in self.items
            if item.enabled
        ]

        next_available = {
            index: time.monotonic()
            for index in range(len(enabled))
        }

        try:
            while not self._stop_event.is_set():
                now = time.monotonic()

                due = [
                    (
                        index,
                        item,
                    )
                    for index, item in enumerate(
                        enabled
                    )
                    if next_available[index] <= now
                ]

                if not due:
                    wait_until = min(
                        next_available.values()
                    )

                    wait_seconds = max(
                        0.05,
                        wait_until - now,
                    )

                    self.status.message = "WAITING"
                    self.status.current_item = ""
                    self.status.next_run_timestamp = (
                        time.time()
                        + wait_seconds
                    )
                    self._emit_status()

                    if self._stop_event.wait(
                        wait_seconds
                    ):
                        break

                    continue

                # Exactly one item is selected at a time.
                # Once selected, it owns the automation lock
                # until its complete cycle succeeds.
                index, item = due[0]

                self.status.current_item = item.name
                self.status.message = (
                    f"RUNNING • {item.name}"
                )
                self.status.next_run_timestamp = None
                self._emit_status()

                succeeded = False
                attempt = 0

                while (
                    not succeeded
                    and not self._stop_event.is_set()
                ):
                    attempt += 1

                    if attempt == 1:
                        message = (
                            f"RUNNING • {item.name}"
                        )
                    else:
                        message = (
                            f"RETRYING • {item.name} "
                            f"(attempt {attempt})"
                        )

                    self.status.message = message
                    self.status.current_item = item.name
                    self._emit_status()

                    try:
                        # Only one automation item can run at a time.
                        # Anti-AFK has higher priority through the shared
                        # priority gate and gets the next available turn.
                        with self._run_lock:
                            if self.priority_gate is not None:
                                self.priority_gate.enter_automation()

                            try:
                                self._run_item(item)
                            finally:
                                if self.priority_gate is not None:
                                    self.priority_gate.leave()

                        succeeded = True

                    except Exception as exc:
                        if self._stop_event.is_set():
                            break

                        self.status.message = (
                            f"RETRY WAIT • {item.name} • "
                            f"{exc}"
                        )
                        self.status.current_item = item.name
                        self._emit_status()

                        # Do not allow another item to run.
                        # The current item keeps ownership until
                        # its cycle succeeds.
                        if self._stop_event.wait(5.0):
                            break

                if self._stop_event.is_set():
                    break

                if succeeded:
                    next_available[index] = (
                        time.monotonic()
                        + max(
                            0.0,
                            item.cooldown_seconds,
                        )
                    )

                    self.status.message = (
                        f"COMPLETE • {item.name}"
                    )
                    self.status.current_item = ""
                    self.status.next_run_timestamp = (
                        time.time()
                        + max(
                            0.0,
                            item.cooldown_seconds,
                        )
                    )
                    self._emit_status()

                    # Give the UI/status thread a moment to see
                    # the completion before another item starts.
                    if self._stop_event.wait(0.20):
                        break

        finally:
            self.status.running = False
            self.status.current_item = ""
            self.status.next_run_timestamp = None

            if (
                self.status.message.startswith("RUNNING")
                or self.status.message.startswith("RETRY")
                or self.status.message == "WAITING"
            ):
                self.status.message = "STOPPED"

            self._emit_status()

    # =========================================================
    # Actual automation sequence
    # =========================================================

    def _run_item(
        self,
        item: AutomationItem,
    ):
        previous = self._get_active_window()

        self.status.previous_window = previous.title
        self._emit_status()

        game = self.find_game_window()

        self.status.game_window = game.title
        self._emit_status()

        self._set_message(
            f"FOCUSING • {game.title}",
            current_item=item.name,
        )

        # Every automation item uses the same shared coordinates.
        coordinates = self.coordinates

        missing = coordinates.missing()
        if missing:
            raise AutomationError(
                "Shared automation coordinates are incomplete: "
                + ", ".join(missing)
            )

        # Focus Sober before ANY input is sent.
        self._activate_window(game)

        time.sleep(self.POST_FOCUS_DELAY)

        try:
            self._set_message(
                f"OPENING INVENTORY • {item.name}",
                current_item=item.name,
            )

            self._click_verified(
                coordinates.inventory,
                "Inventory",
                item,
            )

            self._sleep(
                item.click_delay_seconds,
            )

            self._click_verified(
                coordinates.items,
                "Items",
                item,
            )

            self._sleep(
                item.click_delay_seconds,
            )

            self._click_verified(
                coordinates.search_bar,
                "Search Bar",
                item,
            )

            self._sleep(
                item.click_delay_seconds,
            )

            self._ctrl_a()
            self._sleep(0.05)

            self._type_text(
                item.search_text,
            )

            self._sleep(
                max(
                    item.click_delay_seconds,
                    self.TYPE_SETTLE,
                ),
            )

            self._click_verified(
                coordinates.first_slot,
                "First Slot",
                item,
            )

            self._sleep(
                item.click_delay_seconds,
            )

            self._click_verified(
                coordinates.quantity,
                "Quantity",
                item,
            )

            self._sleep(0.10)

            self._ctrl_a()
            self._sleep(0.05)

            self._type_text("1")

            self._sleep(
                max(
                    item.click_delay_seconds,
                    self.TYPE_SETTLE,
                ),
            )

            self._click_verified(
                coordinates.use_button,
                "Use Button",
                item,
            )

            self._sleep(
                item.post_use_delay_seconds,
            )

            self._click_verified(
                coordinates.close_inventory,
                "Close Inventory",
                item,
            )

            self._sleep(
                item.click_delay_seconds,
            )

            self._set_message(
                f"COMPLETE • {item.name}",
                current_item=item.name,
            )

        except Exception:
            # Always attempt to close/recover focus through
            # the restoration path below.
            raise

        finally:
            self._set_message(
                f"RESTORING • {previous.title}",
                current_item=item.name,
            )

            restore_error: Exception | None = None

            try:
                time.sleep(self.RESTORE_DELAY)
                self._restore_window(previous)

            except Exception as exc:
                restore_error = exc

            self.status.game_window = ""
            self.status.previous_window = ""
            self._emit_status()

            if restore_error is not None:
                raise AutomationError(
                    "Automation finished its game sequence "
                    "but could not restore the previous window: "
                    f"{restore_error}"
                )

    # =========================================================
    # Input helpers
    # =========================================================

    def _run_input(
        self,
        *args: str,
    ):
        backend = self._resolve_input_backend()
        environment = os.environ.copy()

        if backend == "ydotool":
            if self._socket_path is None:
                self._ensure_ydotoold()

            if (
                self._socket_path is None
                or not self._socket_path.exists()
            ):
                raise AutomationError(
                    "SolsRNGCore ydotool socket is unavailable."
                )

            environment["YDOTOOL_SOCKET"] = str(
                self._socket_path
            )

            command = [
                "ydotool",
                *args,
            ]

        else:
            command = [
                "xdotool",
                *args,
            ]

        result = self._run_command(
            command,
            timeout=self.COMMAND_TIMEOUT,
        )

        if result.returncode != 0:
            detail = (
                result.stderr.strip()
                or result.stdout.strip()
                or f"exit code {result.returncode}"
            )

            raise AutomationError(
                f"Input command failed: {detail}"
            )

        return result

    def _retry_input(
        self,
        *args: str,
    ) -> None:
        last_error = ""

        for attempt in range(
            self.RETRIES
        ):
            if self._stop_event.is_set():
                raise AutomationError(
                    "Automation stopped."
                )

            try:
                self._run_input(
                    *args,
                )
                return

            except Exception as exc:
                last_error = str(exc)

                if attempt < self.RETRIES - 1:
                    time.sleep(
                        0.15
                        * (attempt + 1)
                    )

        raise AutomationError(
            f"Input failed after "
            f"{self.RETRIES} attempts: "
            f"{last_error}"
        )

    def _click(
        self,
        coordinate,
    ):
        if coordinate is None:
            raise AutomationError(
                "Missing click coordinate."
            )

        x, y = coordinate
        x = int(x)
        y = int(y)

        # KDE Wayland:
        # Use wdotool for mouse movement/clicks because its
        # KDE backend operates in the compositor's global
        # coordinate space. ydotool --absolute is NOT used
        # for mouse positioning on this platform.
        if self._is_kde_wayland():
            if shutil.which("wdotool") is None:
                raise AutomationError(
                    "wdotool is required for KDE Wayland mouse automation."
                )

            result = self._wdotool(
                "mousemove",
                str(x),
                str(y),
            )

            if result.returncode != 0:
                raise AutomationError(
                    result.stderr.strip()
                    or result.stdout.strip()
                    or "wdotool mousemove failed."
                )

            self._sleep(
                self.CLICK_SETTLE,
            )

            result = self._wdotool(
                "click",
                "1",
            )

            if result.returncode != 0:
                raise AutomationError(
                    result.stderr.strip()
                    or result.stdout.strip()
                    or "wdotool click failed."
                )

            return

        backend = self._resolve_input_backend()

        if backend == "ydotool":
            self._retry_input(
                "mousemove",
                "--absolute",
                str(x),
                str(y),
            )

            self._sleep(
                self.CLICK_SETTLE,
            )

            self._retry_input(
                "click",
                "0xC0",
            )
            return

        self._retry_input(
            "mousemove",
            str(x),
            str(y),
        )

        self._sleep(
            self.CLICK_SETTLE,
        )

        self._retry_input(
            "click",
            "1",
        )

    def _click_verified(
        self,
        coordinate,
        label: str,
        item: AutomationItem,
    ) -> None:
        if coordinate is None:
            raise AutomationError(
                f"{item.name}: {label} coordinate is missing."
            )

        self._set_message(
            f"CLICK • {label} • {item.name}",
            current_item=item.name,
        )

        self._click(
            coordinate,
        )

    def _type_text(
        self,
        text: str,
    ):
        backend = self._resolve_input_backend()

        if backend == "ydotool":
            self._retry_input(
                "type",
                text,
            )
        else:
            self._retry_input(
                "type",
                "--delay",
                "0",
                text,
            )

    def _ctrl_a(self):
        backend = self._resolve_input_backend()

        if backend == "ydotool":
            self._retry_input(
                "key",
                "29:1",
                "30:1",
                "30:0",
                "29:0",
            )
            return

        self._retry_input(
            "key",
            "ctrl+a",
        )

    # =========================================================
    # Compatibility helpers
    # =========================================================

    @staticmethod
    def _sleep(
        seconds: float,
    ):
        if seconds > 0:
            time.sleep(seconds)

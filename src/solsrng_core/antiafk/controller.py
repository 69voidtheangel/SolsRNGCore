from __future__ import annotations

import shutil
import subprocess
import threading
import time
from typing import Callable


class WindowError(RuntimeError):
    """Raised when Anti-AFK cannot perform an input action."""


class AntiAFKController:
    """
    Anti-AFK controller with two modes.

    SPACE:
        Wait for the configured interval, then press Space.

    ALT+TAB:
        Alt+Tab to the next window, press Space, then Alt+Tab back.
    """

    SPACE_MODE = "space"
    ALT_TAB_MODE = "alt_tab"

    def __init__(
        self,
        interval_seconds: float = 120.0,
        method: str = SPACE_MODE,
        log: Callable[[str], None] | None = None,
    ):
        self.interval_seconds = max(1.0, float(interval_seconds))
        self.method = self._normalize_method(method)
        self.log = log or (lambda _: None)

        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

        if shutil.which("ydotool") is None:
            raise WindowError(
                "ydotool is not installed or not in PATH"
            )

    @classmethod
    def _normalize_method(cls, method: str) -> str:
        value = str(method).strip().lower()

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

    @property
    def running(self) -> bool:
        return (
            self._thread is not None
            and self._thread.is_alive()
        )

    @staticmethod
    def _keycode(key: str) -> int:
        keycodes = {
            "tab": 15,
            "space": 57,
            "alt": 56,
        }

        normalized = str(key).strip().lower()

        if normalized not in keycodes:
            raise WindowError(
                f"Unsupported Anti-AFK key: {key}"
            )

        return keycodes[normalized]

    def _ydotool(
        self,
        *key_events: str,
        timeout: float = 5.0,
    ) -> None:
        if not key_events:
            return

        try:
            result = subprocess.run(
                ["ydotool", "key", *key_events],
                text=True,
                capture_output=True,
                check=False,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            raise WindowError(
                "ydotool timed out while sending input"
            )
        except OSError as exc:
            raise WindowError(
                f"Unable to execute ydotool: {exc}"
            )

        if result.returncode != 0:
            error = (
                result.stderr.strip()
                or result.stdout.strip()
                or "unknown ydotool error"
            )
            raise WindowError(error)

    def _press_space(self) -> None:
        code = self._keycode("space")

        self._ydotool(
            f"{code}:1",
            f"{code}:0",
        )

    def _alt_tab_once(self) -> None:
        alt = self._keycode("alt")
        tab = self._keycode("tab")

        self._ydotool(
            f"{alt}:1",
            f"{tab}:1",
            f"{tab}:0",
            f"{alt}:0",
        )

    def _run_space_mode(self) -> None:
        self._press_space()

        self.log(
            "Anti-AFK: Space pressed"
        )

    def _run_alt_tab_mode(self) -> None:
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
                    f"Anti-AFK: failed to Alt+Tab back: {exc}"
                )
                raise

        self.log(
            "Anti-AFK: returned to previous window"
        )

    def _tick(self) -> None:
        if self.method == self.SPACE_MODE:
            self._run_space_mode()
        elif self.method == self.ALT_TAB_MODE:
            self._run_alt_tab_mode()
        else:
            raise WindowError(
                f"Unsupported Anti-AFK method: {self.method}"
            )

    def start(self) -> None:
        if self.running:
            return

        self._stop.clear()

        # Verify that ydotool works before starting the worker.
        if self.method == self.SPACE_MODE:
            self._press_space()
        else:
            self._alt_tab_once()
            time.sleep(0.20)

            try:
                self._press_space()
            finally:
                time.sleep(0.20)
                self._alt_tab_once()

        self._thread = threading.Thread(
            target=self._loop,
            name="SolsRNG-AntiAFK",
            daemon=True,
        )
        self._thread.start()

        mode_name = (
            "Space"
            if self.method == self.SPACE_MODE
            else "Alt+Tab → Space → Alt+Tab"
        )

        self.log(
            f"Anti-AFK started "
            f"(every {self.interval_seconds:g}s, mode={mode_name})"
        )

    def stop(self, restore: bool = True) -> None:
        del restore

        self._stop.set()

        thread = self._thread

        if (
            thread is not None
            and thread is not threading.current_thread()
        ):
            thread.join(timeout=3.0)

            if thread.is_alive():
                self.log(
                    "Anti-AFK worker did not stop within timeout"
                )

        self._thread = None

        self.log("Anti-AFK stopped")

    def _loop(self) -> None:
        while not self._stop.wait(self.interval_seconds):
            try:
                self._tick()

            except WindowError as exc:
                self.log(
                    f"Anti-AFK error: {exc}"
                )

            except Exception as exc:
                self.log(
                    f"Anti-AFK unexpected error: {exc}"
                )

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

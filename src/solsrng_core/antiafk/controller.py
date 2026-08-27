from __future__ import annotations

import shutil
import subprocess
import threading
from typing import Callable


class WindowError(RuntimeError):
    pass


class AntiAFKController:
    """
    Wayland-safe Anti-AFK.

    Does not search for, focus, or switch windows.
    Sends the configured key through ydotool so the
    existing macro can keep control of the game.
    """

    def __init__(
        self,
        interval_seconds: float = 120.0,
        key: str = "space",
        game_title_regex: str = "",
        log: Callable[[str], None] | None = None,
    ):
        self.interval_seconds = max(1.0, float(interval_seconds))
        self.key = key.strip() or "space"
        self.game_title_regex = game_title_regex
        self.log = log or (lambda _: None)

        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

        if shutil.which("ydotool") is None:
            raise WindowError(
                "ydotool is not installed or not in PATH"
            )

    @property
    def running(self) -> bool:
        return (
            self._thread is not None
            and self._thread.is_alive()
        )

    def _send_key(self) -> None:
        """
        Send a press + release using ydotool.

        Common Linux key names are accepted by ydotool,
        e.g. space, enter, w, a, s, d.
        """
        result = subprocess.run(
            ["ydotool", "key", f"{self._keycode(self.key)}:1", f"{self._keycode(self.key)}:0"],
            text=True,
            capture_output=True,
            check=False,
        )

        if result.returncode != 0:
            error = result.stderr.strip() or "unknown ydotool error"
            raise WindowError(error)

    @staticmethod
    def _keycode(key: str) -> int:
        key = key.lower().strip()

        keycodes = {
            "esc": 1,
            "escape": 1,
            "1": 2,
            "2": 3,
            "3": 4,
            "4": 5,
            "5": 6,
            "6": 7,
            "7": 8,
            "8": 9,
            "9": 10,
            "0": 11,
            "minus": 12,
            "equals": 13,
            "backspace": 14,
            "tab": 15,
            "q": 16,
            "w": 17,
            "e": 18,
            "r": 19,
            "t": 20,
            "y": 21,
            "u": 22,
            "i": 23,
            "o": 24,
            "p": 25,
            "leftbracket": 26,
            "rightbracket": 27,
            "enter": 28,
            "return": 28,
            "ctrl": 29,
            "a": 30,
            "s": 31,
            "d": 32,
            "f": 33,
            "g": 34,
            "h": 35,
            "j": 36,
            "k": 37,
            "l": 38,
            "semicolon": 39,
            "apostrophe": 40,
            "grave": 41,
            "shift": 42,
            "backslash": 43,
            "z": 44,
            "x": 45,
            "c": 46,
            "v": 47,
            "b": 48,
            "n": 49,
            "m": 50,
            "comma": 51,
            "period": 52,
            "slash": 53,
            "rightshift": 54,
            "kpasterisk": 55,
            "alt": 56,
            "space": 57,
            "capslock": 58,
            "f1": 59,
            "f2": 60,
            "f3": 61,
            "f4": 62,
            "f5": 63,
            "f6": 64,
            "f7": 65,
            "f8": 66,
            "f9": 67,
            "f10": 68,
            "numlock": 69,
            "scrolllock": 70,
            "f11": 87,
            "f12": 88,
            "rightctrl": 97,
            "rightalt": 100,
            "home": 102,
            "up": 103,
            "pageup": 104,
            "left": 105,
            "right": 106,
            "end": 107,
            "down": 108,
            "pagedown": 109,
            "insert": 110,
            "delete": 111,
        }

        if key.isdigit():
            code = keycodes.get(key)
            if code is not None:
                return code

        if key in keycodes:
            return keycodes[key]

        if len(key) == 1 and key in keycodes:
            return keycodes[key]

        raise WindowError(
            f"Unsupported Anti-AFK key: {key}"
        )

    def swap_to_game(self):
        """
        Kept for compatibility with the GUI.

        Wayland does not need an explicit game-window swap.
        The game should already be the focused window.
        """
        self.log(
            "Anti-AFK: leaving current focus unchanged"
        )
        return None

    def restore_previous_window(self) -> None:
        """
        Kept for GUI compatibility.

        Nothing is restored because Anti-AFK never changes focus.
        """
        return None

    def start(self) -> None:
        if self.running:
            return

        self._stop.clear()

        # Verify that ydotoold/socket is available before starting.
        self._send_key()

        self._thread = threading.Thread(
            target=self._loop,
            name="SolsRNG-AntiAFK",
            daemon=True,
        )
        self._thread.start()

        self.log(
            f"Anti-AFK started "
            f"(every {self.interval_seconds:g}s, key={self.key})"
        )

    def stop(self, restore: bool = True) -> None:
        self._stop.set()

        thread = self._thread

        if (
            thread
            and thread is not threading.current_thread()
        ):
            thread.join(timeout=2.0)

        self._thread = None

        self.log("Anti-AFK stopped")

    def _loop(self) -> None:
        while not self._stop.wait(
            self.interval_seconds
        ):
            try:
                self._send_key()
                self.log(
                    f"Anti-AFK key sent: {self.key}"
                )
            except WindowError as exc:
                self.log(
                    f"Anti-AFK error: {exc}"
                )

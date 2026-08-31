from __future__ import annotations

import json
import re
import threading
from pathlib import Path
from typing import Callable

from solsrng_core.config import BIOMES


DEFAULT_LOG_DIR = (
    Path.home()
    / ".var"
    / "app"
    / "org.vinegarhq.Sober"
    / "data"
    / "sober"
    / "sober_logs"
)


class SoberBiomeWatcher:
    """Monitor Sober logs and emit only real Sol's RNG biome changes."""

    _RPC_RE = re.compile(
        r"\[BloxstrapRPC\]\s+(\{.*\})\s*$"
    )

    def __init__(
        self,
        callback: Callable[[str], None],
        log: Callable[[str], None] | None = None,
        log_path: Path | None = None,
        biome_ended_callback: Callable[[str], None] | None = None,
    ):
        self.callback = callback
        self.log = log or (lambda _: None)
        self.biome_ended_callback = biome_ended_callback

        supplied = (
            log_path.expanduser()
            if log_path is not None
            else DEFAULT_LOG_DIR / "latest.log"
        )

        self.log_dir = (
            supplied.parent
            if supplied.name == "latest.log"
            else supplied.parent
        )

        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._current_biome: str | None = None
        self._initial_state_sent = False

    @property
    def running(self) -> bool:
        return (
            self._thread is not None
            and self._thread.is_alive()
        )

    @property
    def current_biome(self) -> str | None:
        return self._current_biome

    def start(self) -> None:
        if self.running:
            return

        self._stop.clear()

        self._thread = threading.Thread(
            target=self._run,
            name="SolsRNG-SoberLogMonitor",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

        thread = self._thread

        if (
            thread is not None
            and thread is not threading.current_thread()
        ):
            thread.join(timeout=0.2)

        if thread is None or not thread.is_alive():
            self._thread = None

    def _find_newest_log(self) -> Path | None:
        try:
            logs = [
                p
                for p in self.log_dir.glob("*.log")
                if p.is_file()
                and p.name != "latest.log"
            ]

            if not logs:
                return None

            return max(
                logs,
                key=lambda p: p.stat().st_mtime_ns,
            )

        except OSError:
            return None

    def _extract_biome(self, line: str) -> str | None:
        match = self._RPC_RE.search(line)

        if not match:
            return None

        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError:
            return None

        if payload.get("command") != "SetRichPresence":
            return None

        data = payload.get("data")

        if not isinstance(data, dict):
            return None

        large_image = data.get("largeImage")

        if not isinstance(large_image, dict):
            return None

        biome = str(
            large_image.get("hoverText", "")
        ).strip().upper()

        if biome not in BIOMES:
            return None

        return biome

    def _emit_initial_state(self, biome: str) -> None:
        self._current_biome = biome
        self._initial_state_sent = True

        self.log(
            f"Sober current biome: {biome}"
        )

        try:
            self.callback(biome)
        except Exception as exc:
            self.log(
                f"Initial biome callback error: {exc}"
            )

    def _process_biome(self, biome: str) -> None:
        # Repeated RPC updates for the same biome are ignored.
        if biome == self._current_biome:
            return

        previous = self._current_biome
        self._current_biome = biome

        if previous is None:
            self._emit_initial_state(biome)
            return

        self.log(
            f"Sober biome changed: {previous} -> {biome}"
        )

        if self.biome_ended_callback is not None:
            try:
                self.biome_ended_callback(previous)
            except Exception as exc:
                self.log(
                    f"Biome ended callback error: {exc}"
                )

        try:
            self.callback(biome)
        except Exception as exc:
            self.log(
                f"Biome callback error: {exc}"
            )

    def _read_current_state(
        self,
        target: Path,
    ) -> int:
        """
        Read the existing log once, find the LAST valid biome,
        emit it exactly once, then return EOF position.
        """

        last_biome: str | None = None

        try:
            with target.open(
                "r",
                encoding="utf-8",
                errors="replace",
            ) as handle:
                for line in handle:
                    biome = self._extract_biome(line)

                    if biome is not None:
                        last_biome = biome

                position = handle.tell()

        except (OSError, UnicodeError) as exc:
            self.log(
                f"Unable to read current Sober state: {exc}"
            )
            return 0

        if last_biome is not None:
            self._emit_initial_state(last_biome)
        else:
            self.log(
                "No valid Sol's RNG biome found in current Sober log"
            )

        return position

    def _run(self) -> None:
        handle = None
        current_file: Path | None = None
        position = 0

        while not self._stop.is_set():
            try:
                target = self._find_newest_log()

                if target is None:
                    self._stop.wait(0.25)
                    continue

                target = target.resolve(strict=True)

                # New Sober session / new log file.
                if handle is None or current_file != target:
                    if handle is not None:
                        try:
                            handle.close()
                        except OSError:
                            pass

                    # On the first attach, inspect existing history
                    # to determine the current biome immediately.
                    handle = target.open(
                        "r",
                        encoding="utf-8",
                        errors="replace",
                    )

                    current_file = target
                    position = 0

                    if not self._initial_state_sent:
                        handle.close()
                        handle = None

                        position = self._read_current_state(target)

                        handle = target.open(
                            "r",
                            encoding="utf-8",
                            errors="replace",
                        )
                        handle.seek(position)

                    else:
                        # A new Sober log means a new session.
                        # Establish its state from its existing contents.
                        handle.close()
                        handle = None

                        self._initial_state_sent = False
                        self._current_biome = None

                        position = self._read_current_state(target)

                        handle = target.open(
                            "r",
                            encoding="utf-8",
                            errors="replace",
                        )
                        handle.seek(position)

                    self.log(
                        f"Live Sober monitoring: {target.name}"
                    )

                handle.seek(position)

                while not self._stop.is_set():
                    line = handle.readline()

                    if not line:
                        break

                    position = handle.tell()

                    biome = self._extract_biome(line)

                    if biome is not None:
                        self._process_biome(biome)

                newest = self._find_newest_log()

                if newest is not None:
                    try:
                        if newest.resolve() != current_file:
                            continue
                    except OSError:
                        pass

                try:
                    if current_file.stat().st_size < position:
                        handle.seek(0)
                        position = 0
                except OSError:
                    pass

            except (FileNotFoundError, OSError, UnicodeError):
                if handle is not None:
                    try:
                        handle.close()
                    except OSError:
                        pass

                handle = None
                current_file = None
                position = 0

            except Exception as exc:
                self.log(
                    f"Sober monitor error: {exc}"
                )

            self._stop.wait(0.05)

        if handle is not None:
            try:
                handle.close()
            except OSError:
                pass

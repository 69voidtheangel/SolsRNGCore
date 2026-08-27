from __future__ import annotations

import json
import re
import threading
import time
from pathlib import Path
from typing import Callable

from solsrng_core.config import BIOMES


DEFAULT_LOG = (
    Path.home()
    / ".var"
    / "app"
    / "org.vinegarhq.Sober"
    / "data"
    / "sober"
    / "sober_logs"
    / "latest.log"
)


class SoberBiomeWatcher:
    """
    Watches Sober's latest.log and extracts Sol's RNG biome
    changes from Roblox BloxstrapRPC SetRichPresence entries.
    """

    _RPC_RE = re.compile(
        r'\[BloxstrapRPC\]\s+(\{.*\})\s*$'
    )

    def __init__(
        self,
        callback: Callable[[str], None],
        log: Callable[[str], None] | None = None,
        log_path: Path | None = None,
    ):
        self.callback = callback
        self.log = log or (lambda _: None)
        self.log_path = (
            log_path.expanduser()
            if log_path is not None
            else DEFAULT_LOG
        )

        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_biome: str | None = None

    @property
    def running(self) -> bool:
        return (
            self._thread is not None
            and self._thread.is_alive()
        )

    def start(self) -> None:
        if self.running:
            return

        self._stop.clear()

        self._thread = threading.Thread(
            target=self._run,
            name="SolsRNG-SoberLogWatcher",
            daemon=True,
        )
        self._thread.start()

        self.log(
            f"Sober log watcher started: {self.log_path}"
        )

    def stop(self) -> None:
        self._stop.set()

        thread = self._thread

        if (
            thread is not None
            and thread is not threading.current_thread()
        ):
            thread.join(timeout=2.0)

        self._thread = None

    def _extract_biome(self, line: str) -> str | None:
        match = self._RPC_RE.search(line)

        if not match:
            return None

        raw_json = match.group(1)

        try:
            payload = json.loads(raw_json)
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

    def _handle_line(self, line: str) -> None:
        biome = self._extract_biome(line)

        if biome is None:
            return

        if biome == self._last_biome:
            return

        previous = self._last_biome
        self._last_biome = biome

        if previous is None:
            self.log(
                f"Detected current biome: {biome}"
            )
        else:
            self.log(
                f"Biome changed: {previous} -> {biome}"
            )

        try:
            self.callback(biome)
        except Exception as exc:
            self.log(
                f"Biome callback error: {exc}"
            )

    def _run(self) -> None:
        current_target: Path | None = None
        handle = None
        position = 0

        while not self._stop.is_set():
            try:
                target = self.log_path.resolve(
                    strict=True
                )
            except FileNotFoundError:
                self.log_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )
                time.sleep(1.0)
                continue
            except OSError:
                time.sleep(1.0)
                continue

            try:
                if (
                    handle is None
                    or current_target != target
                ):
                    if handle is not None:
                        handle.close()

                    handle = target.open(
                        "r",
                        encoding="utf-8",
                        errors="replace",
                    )

                    current_target = target

                    # Start at EOF so old historical entries
                    # don't immediately spam Discord.
                    handle.seek(0, 2)
                    position = handle.tell()

                    self.log(
                        f"Watching Sober log: {target.name}"
                    )

                handle.seek(position)

                while True:
                    line = handle.readline()

                    if not line:
                        break

                    position = handle.tell()
                    self._handle_line(line)

                # Detect truncation/rotation.
                try:
                    size = target.stat().st_size
                    if size < position:
                        handle.seek(0)
                        position = 0
                except OSError:
                    pass

            except (OSError, UnicodeError) as exc:
                self.log(
                    f"Sober log watcher error: {exc}"
                )

                if handle is not None:
                    try:
                        handle.close()
                    except OSError:
                        pass

                handle = None
                current_target = None
                position = 0

            self._stop.wait(0.5)

        if handle is not None:
            try:
                handle.close()
            except OSError:
                pass

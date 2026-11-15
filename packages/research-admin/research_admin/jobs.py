"""Background job queue for research runs, draft generation, watchlist, and scheduled publishing."""

import threading
from datetime import UTC, datetime


class JobCancelled(RuntimeError):
    """Raised inside a job when the user cancelled it between stages."""


class JobWorker:
    """Runs queued jobs one at a time on a daemon thread with heartbeat and maintenance ticks."""

    def __init__(self, process_next_job, *, poll_seconds: float = 2.0, on_idle_tick=None):
        self._process_next_job = process_next_job
        self._on_idle_tick = on_idle_tick
        self._poll_seconds = max(float(poll_seconds), 0.5)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.last_tick_at: str = ""

    @property
    def running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def start(self) -> None:
        if self.running:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="research-job-worker", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        thread = self._thread
        if thread:
            thread.join(timeout=5)
        self._thread = None

    def _run(self) -> None:
        while not self._stop.is_set():
            self.last_tick_at = datetime.now(UTC).isoformat()
            processed = False
            try:
                processed = self._process_next_job()
            except Exception:  # noqa: BLE001 - a bad job must never kill the worker
                processed = True
            if not processed:
                if callable(self._on_idle_tick):
                    try:
                        self._on_idle_tick()
                    except Exception:  # noqa: BLE001
                        pass
                self._stop.wait(self._poll_seconds)

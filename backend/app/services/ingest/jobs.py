"""In-memory job store with disk-backed artifacts and TTL cleanup.

Ported from the standalone Ingest project. Jobs are deliberately not
persisted to the database: uploads and results are transient scratch data
(self-cleaning, TTL-expired), unlike vault secrets and notes.
"""

from __future__ import annotations

import shutil
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from app.core.config import get_settings


@dataclass
class FileTask:
    id: str
    original_name: str
    upload_path: Path
    output_path: Path | None = None
    status: str = "pending"  # pending | processing | done | error
    error: str | None = None
    output_size: int | None = None
    used_vision: bool = False


@dataclass
class Job:
    id: str
    created_at: float
    files: list[FileTask] = field(default_factory=list)

    @property
    def status(self) -> str:
        statuses = {f.status for f in self.files}
        if statuses <= {"done", "error"}:
            return "failed" if statuses == {"error"} else "done"
        return "processing"

    @property
    def progress(self) -> float:
        if not self.files:
            return 1.0
        finished = sum(1 for f in self.files if f.status in ("done", "error"))
        return finished / len(self.files)

    def dir(self) -> Path:
        return get_settings().ingest_jobs_dir / self.id


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._cleanup_started = False

    def create(self) -> Job:
        job = Job(id=uuid.uuid4().hex, created_at=time.time())
        with self._lock:
            self._jobs[job.id] = job
        (job.dir() / "in").mkdir(parents=True, exist_ok=True)
        (job.dir() / "out").mkdir(parents=True, exist_ok=True)
        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def cleanup_expired(self) -> None:
        cutoff = time.time() - get_settings().ingest_job_ttl_minutes * 60
        with self._lock:
            expired = [j for j in self._jobs.values() if j.created_at < cutoff]
            for job in expired:
                del self._jobs[job.id]
        for job in expired:
            shutil.rmtree(job.dir(), ignore_errors=True)

    def start_cleanup_thread(self) -> None:
        if self._cleanup_started:
            return
        self._cleanup_started = True

        def loop() -> None:
            while True:
                time.sleep(60)
                try:
                    self.cleanup_expired()
                except Exception:
                    pass

        threading.Thread(target=loop, daemon=True, name="ingest-job-cleanup").start()


store = JobStore()

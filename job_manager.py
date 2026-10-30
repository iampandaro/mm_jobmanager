from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional
import uuid


@dataclass(frozen=True)
class Job:
    id: str
    name: str


@dataclass
class ShiftEvent:
    job_id: str
    event_name: str
    trigger_at: datetime
    triggered: bool = False
    triggered_at: Optional[datetime] = None


class JobManager:
    def __init__(self, on_event: Optional[Callable[[ShiftEvent], None]] = None) -> None:
        self._jobs_by_id: Dict[str, Job] = {}
        self._jobs_by_name: Dict[str, Job] = {}
        self._events: List[ShiftEvent] = []
        self._on_event = on_event

    def detect_job(self, job_name: str) -> Job:
        name = job_name.strip()
        if not name:
            raise ValueError("job_name must not be empty")

        existing = self._jobs_by_name.get(name)
        if existing:
            return existing

        job = Job(id=str(uuid.uuid4()), name=name)
        self._jobs_by_name[name] = job
        self._jobs_by_id[job.id] = job
        return job

    def start_shift(
        self,
        job_identifier: str,
        event_name: str,
        trigger_at: Optional[datetime] = None,
    ) -> ShiftEvent:
        job = self._resolve_job(job_identifier)
        when = trigger_at or datetime.now(timezone.utc)
        event = ShiftEvent(job_id=job.id, event_name=event_name, trigger_at=when)
        self._events.append(event)

        if when <= datetime.now(timezone.utc):
            self._trigger(event, datetime.now(timezone.utc))

        return event

    def process_pending_events(self, now: Optional[datetime] = None) -> List[ShiftEvent]:
        current = now or datetime.now(timezone.utc)
        triggered: List[ShiftEvent] = []
        for event in self._events:
            if not event.triggered and event.trigger_at <= current:
                self._trigger(event, current)
                triggered.append(event)
        return triggered

    @property
    def events(self) -> List[ShiftEvent]:
        return list(self._events)

    def _resolve_job(self, job_identifier: str) -> Job:
        by_id = self._jobs_by_id.get(job_identifier)
        if by_id:
            return by_id
        return self.detect_job(job_identifier)

    def _trigger(self, event: ShiftEvent, when: datetime) -> None:
        event.triggered = True
        event.triggered_at = when
        if self._on_event:
            self._on_event(event)

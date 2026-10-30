# mm_jobmanager

Minimal job manager module with:

- `detect_job(job_name)` to identify/register a job
- `start_shift(job_identifier, event_name, trigger_at=None)` to create a shift event
- `process_pending_events(now=None)` to trigger due events

## Quick example

```python
from datetime import datetime, timedelta, timezone
from job_manager import JobManager

manager = JobManager()
job = manager.detect_job("Warehouse")
manager.start_shift(job.id, "clock_in", datetime.now(timezone.utc) + timedelta(minutes=5))

# later...
manager.process_pending_events()
```

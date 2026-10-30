from datetime import datetime, timedelta, timezone
import unittest

from job_manager import JobManager


class JobManagerTests(unittest.TestCase):
    def test_detect_job_reuses_existing_job(self) -> None:
        manager = JobManager()

        first = manager.detect_job("Cashier")
        second = manager.detect_job("Cashier")

        self.assertEqual(first.id, second.id)

    def test_start_shift_schedules_and_triggers_when_due(self) -> None:
        manager = JobManager()
        future = datetime.now(timezone.utc) + timedelta(minutes=10)

        event = manager.start_shift("Barista", "clock_in", trigger_at=future)
        self.assertFalse(event.triggered)

        triggered = manager.process_pending_events(now=future)

        self.assertEqual(1, len(triggered))
        self.assertTrue(triggered[0].triggered)

    def test_start_shift_now_triggers_immediately(self) -> None:
        received = []
        manager = JobManager(on_event=received.append)

        event = manager.start_shift("Manager", "clock_in")

        self.assertTrue(event.triggered)
        self.assertEqual(1, len(received))


if __name__ == "__main__":
    unittest.main()

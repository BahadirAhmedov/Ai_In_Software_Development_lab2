import unittest
from datetime import datetime, timedelta

from reports import ReportNotFoundError, ReportScheduler


class ReportSchedulerTest(unittest.TestCase):
    def setUp(self):
        self.scheduler = ReportScheduler()
        self.future = datetime.now() + timedelta(hours=1)

    def test_schedule_and_get(self):
        report = self.scheduler.schedule("Sales weekly", self.future)
        self.assertEqual(self.scheduler.get(report.id), report)
        self.assertEqual(report.status, "scheduled")

    def test_schedule_rejects_past_time(self):
        with self.assertRaises(ValueError):
            self.scheduler.schedule("Old", datetime.now() - timedelta(minutes=1))

    def test_get_unknown_id(self):
        with self.assertRaises(ReportNotFoundError):
            self.scheduler.get(999)

    def test_run_due_executes_only_due_reports(self):
        due = self.scheduler.schedule("Due", self.future)
        later = self.scheduler.schedule("Later", self.future + timedelta(days=1))
        executed = self.scheduler.run_due(now=self.future)
        self.assertEqual(executed, [due])
        self.assertEqual(later.status, "scheduled")

    def test_cancel_returns_updated_report(self):
        report = self.scheduler.schedule("Sales weekly", self.future)
        cancelled = self.scheduler.cancel(report.id)
        self.assertIs(cancelled, report)
        self.assertEqual(cancelled.status, "cancelled")

    def test_cancelled_report_is_not_executed(self):
        report = self.scheduler.schedule("Sales weekly", self.future)
        self.scheduler.cancel(report.id)
        executed = self.scheduler.run_due(now=self.future)
        self.assertEqual(executed, [])
        self.assertEqual(report.status, "cancelled")

    def test_cancelled_report_remains_accessible(self):
        report = self.scheduler.schedule("Sales weekly", self.future)
        self.scheduler.cancel(report.id)
        self.assertEqual(self.scheduler.get(report.id).status, "cancelled")
        self.assertEqual(self.scheduler.list_reports(), [report])

    def test_cancel_unknown_id(self):
        with self.assertRaises(ReportNotFoundError):
            self.scheduler.cancel(999)

    def test_cancel_done_report_raises(self):
        report = self.scheduler.schedule("Sales weekly", self.future)
        self.scheduler.run_due(now=self.future)
        with self.assertRaises(ValueError):
            self.scheduler.cancel(report.id)
        self.assertEqual(report.status, "done")

    def test_cancel_is_idempotent(self):
        report = self.scheduler.schedule("Sales weekly", self.future)
        self.scheduler.cancel(report.id)
        again = self.scheduler.cancel(report.id)
        self.assertEqual(again.status, "cancelled")

    def test_cancel_does_not_affect_other_reports(self):
        cancelled = self.scheduler.schedule("Cancelled", self.future)
        other = self.scheduler.schedule("Other", self.future)
        self.scheduler.cancel(cancelled.id)
        executed = self.scheduler.run_due(now=self.future)
        self.assertEqual(executed, [other])
        self.assertEqual(other.status, "done")
        self.assertEqual(cancelled.status, "cancelled")


if __name__ == "__main__":
    unittest.main()

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


if __name__ == "__main__":
    unittest.main()

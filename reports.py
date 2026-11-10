"""Минимальный сервис планирования отчётов (хранение в памяти)."""

from dataclasses import dataclass
from datetime import datetime
from itertools import count


class ReportNotFoundError(Exception):
    pass


@dataclass
class ScheduledReport:
    id: int
    name: str
    run_at: datetime
    status: str = "scheduled"  # scheduled | done | cancelled


class ReportScheduler:
    def __init__(self):
        self._reports: dict[int, ScheduledReport] = {}
        self._ids = count(1)

    def schedule(self, name: str, run_at: datetime) -> ScheduledReport:
        if not name.strip():
            raise ValueError("name must not be empty")
        if run_at <= datetime.now():
            raise ValueError("run_at must be in the future")
        report = ScheduledReport(next(self._ids), name, run_at)
        self._reports[report.id] = report
        return report

    def get(self, report_id: int) -> ScheduledReport:
        try:
            return self._reports[report_id]
        except KeyError:
            raise ReportNotFoundError(report_id) from None

    def cancel(self, report_id: int) -> ScheduledReport:
        """Отменяет запланированный отчёт; повторная отмена ничего не делает."""
        report = self.get(report_id)
        if report.status == "done":
            raise ValueError("cannot cancel a report that has already run")
        report.status = "cancelled"
        return report

    def list_reports(self) -> list[ScheduledReport]:
        return sorted(self._reports.values(), key=lambda r: r.run_at)

    def run_due(self, now: datetime | None = None) -> list[ScheduledReport]:
        """Выполняет все отчёты, время которых наступило."""
        now = now or datetime.now()
        executed = []
        for report in self.list_reports():
            if report.status == "scheduled" and report.run_at <= now:
                report.status = "done"
                executed.append(report)
        return executed

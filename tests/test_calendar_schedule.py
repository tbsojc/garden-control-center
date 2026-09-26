from datetime import date

from app.models.task import Task
from app.services.task_schedule import get_task_dates_for_month


def test_once_task_appears_in_month():
    task = Task(
        execution_type="once",
        due_date=date(2026, 10, 15),
        completed=False,
    )

    dates = get_task_dates_for_month(
        task,
        year=2026,
        month=10,
        today=date(2026, 9, 26),
    )

    assert dates == [
        date(2026, 10, 15),
    ]


def test_once_task_does_not_appear_in_other_month():
    task = Task(
        execution_type="once",
        due_date=date(2026, 10, 15),
        completed=False,
    )

    dates = get_task_dates_for_month(
        task,
        year=2026,
        month=11,
        today=date(2026, 9, 26),
    )

    assert dates == []


def test_completed_once_task_does_not_appear():
    task = Task(
        execution_type="once",
        due_date=date(2026, 10, 15),
        completed=True,
    )

    dates = get_task_dates_for_month(
        task,
        year=2026,
        month=10,
        today=date(2026, 9, 26),
    )

    assert dates == []


def test_recurring_task_has_multiple_dates():
    task = Task(
        execution_type="recurring",
        interval_days=7,
        start_month=1,
        end_month=12,
        last_completed_at=date(2026, 9, 25),
    )

    dates = get_task_dates_for_month(
        task,
        year=2026,
        month=10,
        today=date(2026, 9, 26),
    )

    assert dates == [
        date(2026, 10, 2),
        date(2026, 10, 9),
        date(2026, 10, 16),
        date(2026, 10, 23),
        date(2026, 10, 30),
    ]


def test_recurring_task_respects_season():
    task = Task(
        execution_type="recurring",
        interval_days=7,
        start_month=4,
        end_month=9,
        last_completed_at=date(2026, 9, 25),
    )

    dates = get_task_dates_for_month(
        task,
        year=2026,
        month=10,
        today=date(2026, 9, 26),
    )

    assert dates == []


def test_recurring_task_across_year_end():
    task = Task(
        execution_type="recurring",
        interval_days=7,
        start_month=11,
        end_month=2,
        last_completed_at=date(2026, 12, 25),
    )

    dates = get_task_dates_for_month(
        task,
        year=2027,
        month=1,
        today=date(2026, 12, 26),
    )

    assert dates == [
        date(2027, 1, 1),
        date(2027, 1, 8),
        date(2027, 1, 15),
        date(2027, 1, 22),
        date(2027, 1, 29),
    ]

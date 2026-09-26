from datetime import date

from app.models.task import Task
from app.services.task_schedule import (
    get_next_due_date,
    month_is_active,
    next_active_date,
    get_due_status,
)


# --------------------------------------------------
# month_is_active
# --------------------------------------------------


def test_month_is_active_normal_period():
    assert month_is_active(5, 4, 8) is True
    assert month_is_active(4, 4, 8) is True
    assert month_is_active(8, 4, 8) is True

    assert month_is_active(3, 4, 8) is False
    assert month_is_active(9, 4, 8) is False


def test_month_is_active_across_year_end():
    assert month_is_active(11, 11, 2) is True
    assert month_is_active(12, 11, 2) is True
    assert month_is_active(1, 11, 2) is True
    assert month_is_active(2, 11, 2) is True

    assert month_is_active(3, 11, 2) is False
    assert month_is_active(10, 11, 2) is False


# --------------------------------------------------
# next_active_date
# --------------------------------------------------


def test_next_active_date_inside_season():
    task = Task(
        execution_type="recurring",
        interval_days=7,
        start_month=4,
        end_month=8,
    )

    result = next_active_date(
        task,
        date(2026, 5, 15),
    )

    assert result == date(2026, 5, 15)


def test_next_active_date_before_season():
    task = Task(
        execution_type="recurring",
        interval_days=7,
        start_month=4,
        end_month=8,
    )

    result = next_active_date(
        task,
        date(2026, 2, 15),
    )

    assert result == date(2026, 4, 1)


def test_next_active_date_after_season():
    task = Task(
        execution_type="recurring",
        interval_days=7,
        start_month=4,
        end_month=8,
    )

    result = next_active_date(
        task,
        date(2026, 10, 15),
    )

    assert result == date(2027, 4, 1)


def test_next_active_date_across_year_end():
    task = Task(
        execution_type="recurring",
        interval_days=7,
        start_month=11,
        end_month=2,
    )

    result = next_active_date(
        task,
        date(2026, 10, 15),
    )

    assert result == date(2026, 11, 1)


# --------------------------------------------------
# Einmalige Aufgaben
# --------------------------------------------------


def test_once_task_returns_due_date():
    task = Task(
        execution_type="once",
        due_date=date(2026, 10, 10),
        completed=False,
    )

    result = get_next_due_date(
        task,
        today=date(2026, 9, 26),
    )

    assert result == date(2026, 10, 10)


def test_completed_once_task_has_no_due_date():
    task = Task(
        execution_type="once",
        due_date=date(2026, 10, 10),
        completed=True,
    )

    result = get_next_due_date(
        task,
        today=date(2026, 9, 26),
    )

    assert result is None


# --------------------------------------------------
# Wiederkehrende Aufgaben
# --------------------------------------------------


def test_recurring_task_without_completion_is_due_today_in_active_season():
    task = Task(
        execution_type="recurring",
        interval_days=7,
        start_month=4,
        end_month=10,
        last_completed_at=None,
    )

    result = get_next_due_date(
        task,
        today=date(2026, 9, 26),
    )

    assert result == date(2026, 9, 26)


def test_recurring_task_without_completion_waits_for_season():
    task = Task(
        execution_type="recurring",
        interval_days=7,
        start_month=4,
        end_month=8,
        last_completed_at=None,
    )

    result = get_next_due_date(
        task,
        today=date(2026, 9, 26),
    )

    assert result == date(2027, 4, 1)


def test_recurring_task_uses_interval_after_completion():
    task = Task(
        execution_type="recurring",
        interval_days=14,
        start_month=4,
        end_month=10,
        last_completed_at=date(2026, 9, 20),
    )

    result = get_next_due_date(
        task,
        today=date(2026, 9, 26),
    )

    assert result == date(2026, 10, 4)


def test_recurring_task_moves_candidate_to_next_season():
    task = Task(
        execution_type="recurring",
        interval_days=14,
        start_month=4,
        end_month=9,
        last_completed_at=date(2026, 9, 25),
    )

    result = get_next_due_date(
        task,
        today=date(2026, 9, 26),
    )

    assert result == date(2027, 4, 1)


def test_recurring_task_across_year_end():
    task = Task(
        execution_type="recurring",
        interval_days=14,
        start_month=11,
        end_month=2,
        last_completed_at=date(2026, 12, 20),
    )

    result = get_next_due_date(
        task,
        today=date(2026, 12, 21),
    )

    assert result == date(2027, 1, 3)


def test_recurring_task_without_interval_has_no_due_date():
    task = Task(
        execution_type="recurring",
        interval_days=None,
        start_month=4,
        end_month=10,
    )

    result = get_next_due_date(
        task,
        today=date(2026, 9, 26),
    )

    assert result is None


# --------------------------------------------------
# Automatisierung / ungültiger Typ
# --------------------------------------------------


def test_automation_has_no_due_date_yet():
    task = Task(
        execution_type="automation",
    )

    result = get_next_due_date(
        task,
        today=date(2026, 9, 26),
    )

    assert result is None


def test_unknown_execution_type_has_no_due_date():
    task = Task(
        execution_type="unknown",
    )

    result = get_next_due_date(
        task,
        today=date(2026, 9, 26),
    )

    assert result is None


def test_due_status_overdue():
    status = get_due_status(
        date(2026, 9, 20),
        today=date(2026, 9, 26),
    )

    assert status == {
        "status": "overdue",
        "label": "6 Tage überfällig",
        "days": -6,
    }


def test_due_status_today():
    status = get_due_status(
        date(2026, 9, 26),
        today=date(2026, 9, 26),
    )

    assert status["status"] == "today"
    assert status["label"] == "Heute fällig"


def test_due_status_tomorrow():
    status = get_due_status(
        date(2026, 9, 27),
        today=date(2026, 9, 26),
    )

    assert status["status"] == "tomorrow"
    assert status["label"] == "Morgen fällig"


def test_due_status_upcoming():
    status = get_due_status(
        date(2026, 10, 3),
        today=date(2026, 9, 26),
    )

    assert status["status"] == "upcoming"
    assert status["days"] == 7


def test_due_status_without_date():
    assert get_due_status(None) is None

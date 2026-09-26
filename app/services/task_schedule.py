from datetime import date, timedelta

from app.models.task import Task


def month_is_active(
    month: int,
    start_month: int,
    end_month: int,
) -> bool:
    """
    Prüft, ob ein Monat innerhalb des Saisonzeitraums liegt.

    Unterstützt auch Zeiträume über den Jahreswechsel:
    November bis Februar = 11 -> 2
    """

    if start_month <= end_month:
        return start_month <= month <= end_month

    return month >= start_month or month <= end_month


def first_day_of_active_period(
    task: Task,
    year: int,
) -> date:
    """
    Liefert den ersten möglichen Tag einer Saison.
    """

    if task.start_month is None:
        return date(year, 1, 1)

    return date(
        year,
        task.start_month,
        1,
    )


def next_active_date(
    task: Task,
    start_date: date,
) -> date:
    """
    Sucht ab start_date den nächsten Tag,
    der innerhalb des Saisonzeitraums liegt.
    """

    if (
        task.start_month is None
        or task.end_month is None
    ):
        return start_date

    current = start_date

    # Maximal etwas mehr als ein Jahr suchen.
    for _ in range(370):

        if month_is_active(
            current.month,
            task.start_month,
            task.end_month,
        ):
            return current

        current += timedelta(days=1)

    return start_date


def get_next_due_date(
    task: Task,
    today: date | None = None,
) -> date | None:
    """
    Berechnet den nächsten Fälligkeitstermin einer Aufgabe.
    """

    if today is None:
        today = date.today()

    # ----------------------------------------------
    # Einmalig
    # ----------------------------------------------

    if task.execution_type == "once":

        if task.completed:
            return None

        return task.due_date

    # ----------------------------------------------
    # Automatisierung
    # Noch keine echte Logik
    # ----------------------------------------------

    if task.execution_type == "automation":
        return None

    # ----------------------------------------------
    # Regelmäßig
    # ----------------------------------------------

    if task.execution_type != "recurring":
        return None

    if not task.interval_days:
        return None

    # Noch nie erledigt:
    # erster aktiver Tag ab heute
    if task.last_completed_at is None:

        return next_active_date(
            task,
            today,
        )

    candidate = (
        task.last_completed_at
        + timedelta(days=task.interval_days)
    )

    return next_active_date(
        task,
        candidate,
    )

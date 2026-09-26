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

def get_task_dates_for_month(
    task: Task,
    year: int,
    month: int,
    today: date | None = None,
) -> list[date]:
    """
    Liefert alle Termine einer Aufgabe innerhalb eines Monats.
    """

    if today is None:
        today = date.today()

    month_start = date(year, month, 1)

    if month == 12:
        next_month_start = date(year + 1, 1, 1)
    else:
        next_month_start = date(year, month + 1, 1)

    month_end = next_month_start - timedelta(days=1)

    # ----------------------------------------------
    # Einmalig
    # ----------------------------------------------

    if task.execution_type == "once":

        if task.completed:
            return []

        if task.due_date is None:
            return []

        if month_start <= task.due_date <= month_end:
            return [task.due_date]

        return []

    # ----------------------------------------------
    # Automatisierung
    # Noch keine echte Kalenderlogik
    # ----------------------------------------------

    if task.execution_type == "automation":
        return []

    # ----------------------------------------------
    # Regelmäßig
    # ----------------------------------------------

    if task.execution_type != "recurring":
        return []

    if not task.interval_days:
        return []

    # Noch nie erledigt:
    # Rhythmus beginnt am ersten aktiven Tag ab heute.
    if task.last_completed_at is None:
        current = next_active_date(
            task,
            max(today, month_start),
        )

    else:
        current = next_active_date(
            task,
            task.last_completed_at
            + timedelta(days=task.interval_days),
        )

        # Liegt der nächste Termin vor dem gewünschten Monat,
        # den Rhythmus bis zum Monat weiterführen.
        while current < month_start:
            candidate = (
                current
                + timedelta(days=task.interval_days)
            )

            current = next_active_date(
                task,
                candidate,
            )

    dates = []

    # Alle Termine innerhalb des gewünschten Monats sammeln.
    while current <= month_end:

        if current >= month_start:
            dates.append(current)

        candidate = (
            current
            + timedelta(days=task.interval_days)
        )

        next_date = next_active_date(
            task,
            candidate,
        )

        # Sicherheitsabbruch gegen Endlosschleifen.
        if next_date <= current:
            break

        current = next_date

    return dates


def get_due_status(
    due_date: date | None,
    today: date | None = None,
) -> dict | None:
    """
    Liefert den Fälligkeitsstatus für ein Datum.
    """

    if due_date is None:
        return None

    if today is None:
        today = date.today()

    days_until_due = (
        due_date - today
    ).days

    if days_until_due < 0:
        overdue_days = abs(days_until_due)

        if overdue_days == 1:
            label = "1 Tag überfällig"
        else:
            label = f"{overdue_days} Tage überfällig"

        return {
            "status": "overdue",
            "label": label,
            "days": days_until_due,
        }

    if days_until_due == 0:
        return {
            "status": "today",
            "label": "Heute fällig",
            "days": 0,
        }

    if days_until_due == 1:
        return {
            "status": "tomorrow",
            "label": "Morgen fällig",
            "days": 1,
        }

    return {
        "status": "upcoming",
        "label": f"In {days_until_due} Tagen",
        "days": days_until_due,
    }

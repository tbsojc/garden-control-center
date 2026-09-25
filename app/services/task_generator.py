#from calendar import monthrange
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models import CareRule, Plant, Task


GENERATION_DAYS = 30


def month_is_active(
    month: int,
    start_month: int,
    end_month: int,
) -> bool:
    """
    Prüft, ob ein Monat innerhalb einer Pflegesaison liegt.

    Unterstützt auch Zeiträume über den Jahreswechsel:
    Oktober bis März = 10 -> 3
    """

    if start_month <= end_month:
        return start_month <= month <= end_month

    return month >= start_month or month <= end_month


def rule_is_active_on_date(
    rule: CareRule,
    target_date: date,
) -> bool:
    return month_is_active(
        target_date.month,
        rule.start_month,
        rule.end_month,
    )


def task_already_exists(
    db: Session,
    plant_id: int,
    care_rule_id: int,
    due_date: date,
) -> bool:
    existing_task = (
        db.query(Task)
        .filter(
            Task.plant_id == plant_id,
            Task.care_rule_id == care_rule_id,
            Task.due_date == due_date,
            Task.source == "automatic",
        )
        .first()
    )

    return existing_task is not None


def create_automatic_task(
    db: Session,
    plant: Plant,
    rule: CareRule,
    due_date: date,
) -> bool:
    if task_already_exists(
        db=db,
        plant_id=plant.id,
        care_rule_id=rule.id,
        due_date=due_date,
    ):
        return False

    task = Task(
        title=rule.title,
        description=rule.description,
        due_date=due_date,
        priority=rule.priority,
        source="automatic",
        plant_id=plant.id,
        garden_area_id=plant.garden_area_id,
        care_rule_id=rule.id,
    )

    db.add(task)

    return True


def generate_interval_tasks(
    db: Session,
    plant: Plant,
    rule: CareRule,
    start_date: date,
    end_date: date,
) -> int:
    created_count = 0

    interval = rule.interval_days or 1

    current_date = start_date

    while current_date <= end_date:

        if rule_is_active_on_date(
            rule,
            current_date,
        ):
            created = create_automatic_task(
                db=db,
                plant=plant,
                rule=rule,
                due_date=current_date,
            )

            if created:
                created_count += 1

        current_date += timedelta(days=interval)

    return created_count


def generate_single_task(
    db: Session,
    plant: Plant,
    rule: CareRule,
    start_date: date,
    end_date: date,
) -> int:
    """
    Regeln ohne Wiederholungsintervall bekommen innerhalb
    des Planungsfensters höchstens eine Aufgabe.
    """

    current_date = start_date

    while current_date <= end_date:

        if rule_is_active_on_date(
            rule,
            current_date,
        ):
            created = create_automatic_task(
                db=db,
                plant=plant,
                rule=rule,
                due_date=current_date,
            )

            if created:
                return 1

            return 0

        current_date += timedelta(days=1)

    return 0


def generate_tasks(
    db: Session,
    start_date: date | None = None,
    days: int = GENERATION_DAYS,
) -> int:
    """
    Erzeugt automatische Aufgaben für konkrete Pflanzen.

    Es werden nur Pflanzen berücksichtigt, denen ein
    Pflanzenwissen-Eintrag zugeordnet wurde.
    """

    if start_date is None:
        start_date = date.today()

    end_date = start_date + timedelta(
        days=days - 1
    )

    plants = (
        db.query(Plant)
        .filter(Plant.species_id.is_not(None))
        .all()
    )

    created_count = 0

    for plant in plants:

        if plant.species is None:
            continue

        for rule in plant.species.care_rules:

            if rule.interval_days:
                created_count += generate_interval_tasks(
                    db=db,
                    plant=plant,
                    rule=rule,
                    start_date=start_date,
                    end_date=end_date,
                )

            else:
                created_count += generate_single_task(
                    db=db,
                    plant=plant,
                    rule=rule,
                    start_date=start_date,
                    end_date=end_date,
                )

    db.commit()

    return created_count

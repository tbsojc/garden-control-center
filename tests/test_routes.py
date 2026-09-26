def test_health(client):
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "version" in data


def test_tasks_page(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert "Aufgaben" in response.text


from datetime import date

from app.models import Task


def test_create_once_task(client, db_session):
    response = client.post(
        "/tasks",
        data={
            "title": "Rasen mähen",
            "execution_type": "once",
            "due_date": "2026-10-05",
            "interval_days": "",
            "start_month": "",
            "end_month": "",
            "priority": "normal",
            "garden_area_id": "",
            "plant_id": "",
            "description": "Testaufgabe",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/tasks"

    tasks = db_session.query(Task).all()

    assert len(tasks) == 1

    task = tasks[0]

    assert task.title == "Rasen mähen"
    assert task.execution_type == "once"
    assert task.due_date == date(2026, 10, 5)
    assert task.interval_days is None
    assert task.start_month is None
    assert task.end_month is None
    assert task.priority == "normal"
    assert task.description == "Testaufgabe"
    assert task.completed is False


def test_create_recurring_task(client, db_session):
    response = client.post(
        "/tasks",
        data={
            "title": "Tomaten gießen",
            "execution_type": "recurring",
            "due_date": "",
            "interval_days": "3",
            "start_month": "5",
            "end_month": "9",
            "priority": "high",
            "garden_area_id": "",
            "plant_id": "",
            "description": "Regelmäßig kontrollieren",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303

    task = db_session.query(Task).one()

    assert task.title == "Tomaten gießen"
    assert task.execution_type == "recurring"
    assert task.due_date is None
    assert task.interval_days == 3
    assert task.start_month == 5
    assert task.end_month == 9
    assert task.priority == "high"
    assert task.description == "Regelmäßig kontrollieren"


def test_invalid_once_task_is_not_created(client, db_session):
    response = client.post(
        "/tasks",
        data={
            "title": "Ungültige Aufgabe",
            "execution_type": "once",
            "due_date": "",
            "interval_days": "",
            "start_month": "",
            "end_month": "",
            "priority": "normal",
            "garden_area_id": "",
            "plant_id": "",
            "description": "",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/tasks"

    assert db_session.query(Task).count() == 0


def test_invalid_recurring_task_is_not_created(client, db_session):
    response = client.post(
        "/tasks",
        data={
            "title": "Ungültige Wiederholung",
            "execution_type": "recurring",
            "due_date": "",
            "interval_days": "",
            "start_month": "5",
            "end_month": "9",
            "priority": "normal",
            "garden_area_id": "",
            "plant_id": "",
            "description": "",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303

    assert db_session.query(Task).count() == 0

def test_edit_task(client, db_session):
    task = Task(
        title="Alter Titel",
        execution_type="once",
        due_date=date(2026, 10, 5),
        priority="normal",
        completed=False,
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.post(
        f"/tasks/{task.id}/edit",
        data={
            "title": "Neuer Titel",
            "execution_type": "once",
            "due_date": "2026-10-15",
            "interval_days": "",
            "start_month": "",
            "end_month": "",
            "priority": "high",
            "garden_area_id": "",
            "plant_id": "",
            "description": "Geänderte Beschreibung",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/tasks"

    db_session.refresh(task)

    assert task.title == "Neuer Titel"
    assert task.due_date == date(2026, 10, 15)
    assert task.priority == "high"
    assert task.description == "Geänderte Beschreibung"


def test_change_execution_type_resets_status(client, db_session):
    task = Task(
        title="Testaufgabe",
        execution_type="once",
        due_date=date(2026, 10, 5),
        priority="normal",
        completed=True,
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.post(
        f"/tasks/{task.id}/edit",
        data={
            "title": "Testaufgabe",
            "execution_type": "recurring",
            "due_date": "",
            "interval_days": "7",
            "start_month": "4",
            "end_month": "10",
            "priority": "normal",
            "garden_area_id": "",
            "plant_id": "",
            "description": "",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303

    db_session.refresh(task)

    assert task.execution_type == "recurring"
    assert task.completed is False
    assert task.completed_at is None
    assert task.last_completed_at is None

    assert task.due_date is None
    assert task.interval_days == 7
    assert task.start_month == 4
    assert task.end_month == 10


def test_toggle_once_task(client, db_session):
    task = Task(
        title="Einmalige Aufgabe",
        execution_type="once",
        due_date=date(2026, 10, 5),
        priority="normal",
        completed=False,
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.post(
        f"/tasks/{task.id}/toggle",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/tasks"

    db_session.refresh(task)

    assert task.completed is True
    assert task.completed_at is not None


def test_toggle_once_task_twice_reopens_task(client, db_session):
    task = Task(
        title="Einmalige Aufgabe",
        execution_type="once",
        due_date=date(2026, 10, 5),
        priority="normal",
        completed=False,
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    client.post(
        f"/tasks/{task.id}/toggle",
        follow_redirects=False,
    )

    client.post(
        f"/tasks/{task.id}/toggle",
        follow_redirects=False,
    )

    db_session.refresh(task)

    assert task.completed is False
    assert task.completed_at is None


def test_toggle_recurring_task_records_completion(client, db_session):
    task = Task(
        title="Wiederkehrende Aufgabe",
        execution_type="recurring",
        interval_days=7,
        start_month=4,
        end_month=10,
        priority="normal",
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.post(
        f"/tasks/{task.id}/toggle",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/tasks"

    db_session.refresh(task)

    assert task.last_completed_at == date.today()
    assert task.completed is False
    assert task.completed_at is None


def test_delete_task(client, db_session):
    task = Task(
        title="Zu löschen",
        execution_type="once",
        due_date=date(2026, 10, 5),
        priority="normal",
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    task_id = task.id

    response = client.post(
        f"/tasks/{task_id}/delete",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/tasks"

    assert db_session.get(Task, task_id) is None

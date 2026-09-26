from datetime import date, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import APP_NAME, APP_VERSION
from app.database import get_db
from app.models import GardenArea, Plant, Task
from app.services.task_schedule import get_next_due_date


BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter()

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)

def parse_task_schedule(
    execution_type: str,
    due_date: str,
    interval_days: str,
    start_month: str,
    end_month: str,
):
    if execution_type not in {
        "once",
        "recurring",
        "automation",
    }:
        execution_type = "once"

    task_due_date = None
    task_interval = None
    task_start_month = None
    task_end_month = None

    if execution_type == "once":
        if not due_date:
            return None

        task_due_date = date.fromisoformat(due_date)

    elif execution_type == "recurring":
        if (
            not interval_days
            or not start_month
            or not end_month
        ):
            return None

        task_interval = max(
            1,
            int(interval_days),
        )

        task_start_month = int(start_month)
        task_end_month = int(end_month)

        if not 1 <= task_start_month <= 12:
            return None

        if not 1 <= task_end_month <= 12:
            return None

    return {
        "execution_type": execution_type,
        "due_date": task_due_date,
        "interval_days": task_interval,
        "start_month": task_start_month,
        "end_month": task_end_month,
    }

# --------------------------------------------------
# Aufgaben
# --------------------------------------------------


@router.get("/tasks", response_class=HTMLResponse)
async def tasks(
    request: Request,
    db: Session = Depends(get_db),
):
    all_tasks = db.query(Task).all()

    today = date.today()

    task_due_dates = {}
    task_due_status = {}

    for task in all_tasks:
        due_date = get_next_due_date(
            task,
            today=today,
        )

        task_due_dates[task.id] = due_date

        if due_date is None:
            task_due_status[task.id] = None
            continue

        days_until_due = (
            due_date - today
        ).days

        if days_until_due < 0:
            overdue_days = abs(days_until_due)

            if overdue_days == 1:
                label = "1 Tag überfällig"
            else:
                label = f"{overdue_days} Tage überfällig"

            task_due_status[task.id] = {
                "status": "overdue",
                "label": label,
                "days": days_until_due,
            }

        elif days_until_due == 0:
            task_due_status[task.id] = {
                "status": "today",
                "label": "Heute fällig",
                "days": 0,
            }

        elif days_until_due == 1:
            task_due_status[task.id] = {
                "status": "tomorrow",
                "label": "Morgen fällig",
                "days": 1,
            }

        else:
            task_due_status[task.id] = {
                "status": "upcoming",
                "label": f"In {days_until_due} Tagen",
                "days": days_until_due,
            }

    all_tasks.sort(
        key=lambda task: (
            task.completed,
            task_due_dates[task.id] or date.max,
        )
    )

    areas = (
        db.query(GardenArea)
        .order_by(GardenArea.name)
        .all()
    )

    plants = (
        db.query(Plant)
        .order_by(Plant.name)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="tasks.html",
        context={
            "page": "tasks",
            "app_name": APP_NAME,
            "version": APP_VERSION,
            "tasks": all_tasks,
            "task_due_dates": task_due_dates,
            "task_due_status": task_due_status,
            "areas": areas,
            "plants": plants,
            "today": today,
        },
    )

@router.post("/tasks")
async def create_task(
    title: str = Form(...),
    execution_type: str = Form("once"),
    due_date: str = Form(""),
    interval_days: str = Form(""),
    start_month: str = Form(""),
    end_month: str = Form(""),
    priority: str = Form("normal"),
    garden_area_id: str = Form(""),
    plant_id: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    schedule = parse_task_schedule(
        execution_type=execution_type,
        due_date=due_date,
        interval_days=interval_days,
        start_month=start_month,
        end_month=end_month,
    )

    if schedule is None:
        return RedirectResponse(
            "/tasks",
            status_code=303,
        )

    task = Task(
        title=title.strip(),
        execution_type=schedule["execution_type"],
        due_date=schedule["due_date"],
        interval_days=schedule["interval_days"],
        start_month=schedule["start_month"],
        end_month=schedule["end_month"],
        priority=priority,
        garden_area_id=(
            int(garden_area_id)
            if garden_area_id
            else None
        ),
        plant_id=(
            int(plant_id)
            if plant_id
            else None
        ),
        description=description.strip() or None,
    )

    db.add(task)
    db.commit()

    return RedirectResponse(
        "/tasks",
        status_code=303,
    )


@router.get(
    "/tasks/{task_id}/edit",
    response_class=HTMLResponse,
)
async def edit_task_page(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)

    if task is None:
        return RedirectResponse(
            "/tasks",
            status_code=303,
        )

    areas = (
        db.query(GardenArea)
        .order_by(GardenArea.name)
        .all()
    )

    plants = (
        db.query(Plant)
        .order_by(Plant.name)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="edit_task.html",
        context={
            "page": "edit_task",
            "app_name": APP_NAME,
            "version": APP_VERSION,
            "task": task,
            "areas": areas,
            "plants": plants,
        },
    )

@router.post("/tasks/{task_id}/edit")
async def edit_task(
    task_id: int,
    title: str = Form(...),
    execution_type: str = Form("once"),
    due_date: str = Form(""),
    interval_days: str = Form(""),
    start_month: str = Form(""),
    end_month: str = Form(""),
    priority: str = Form("normal"),
    garden_area_id: str = Form(""),
    plant_id: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)

    if task is None:
        return RedirectResponse(
            "/tasks",
            status_code=303,
        )

    schedule = parse_task_schedule(
        execution_type=execution_type,
        due_date=due_date,
        interval_days=interval_days,
        start_month=start_month,
        end_month=end_month,
    )

    if schedule is None:
        return RedirectResponse(
            f"/tasks/{task_id}/edit",
            status_code=303,
        )

    old_execution_type = task.execution_type

    task.title = title.strip()
    task.execution_type = schedule["execution_type"]
    task.due_date = schedule["due_date"]
    task.interval_days = schedule["interval_days"]
    task.start_month = schedule["start_month"]
    task.end_month = schedule["end_month"]
    task.priority = priority

    task.garden_area_id = (
        int(garden_area_id)
        if garden_area_id
        else None
    )

    task.plant_id = (
        int(plant_id)
        if plant_id
        else None
    )

    task.description = (
        description.strip() or None
    )

    # Beim Wechsel der Ausführungsart
    # alte Statuswerte zurücksetzen.
    if old_execution_type != schedule["execution_type"]:
        task.completed = False
        task.completed_at = None
        task.last_completed_at = None

    db.commit()

    return RedirectResponse(
        "/tasks",
        status_code=303,
    )


@router.post("/tasks/{task_id}/toggle")
async def toggle_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)

    if not task:
        return RedirectResponse(
            "/tasks",
            status_code=303,
        )

    if task.execution_type == "recurring":

        task.last_completed_at = date.today()
        task.completed = False
        task.completed_at = None

    elif task.execution_type == "once":

        task.completed = not task.completed

        if task.completed:
            task.completed_at = datetime.now()
        else:
            task.completed_at = None

    db.commit()

    return RedirectResponse(
        "/tasks",
        status_code=303,
    )


@router.post("/tasks/{task_id}/delete")
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)

    if task:
        db.delete(task)
        db.commit()

    return RedirectResponse(
        "/tasks",
        status_code=303,
    )

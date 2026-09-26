import calendar
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import APP_NAME, APP_VERSION
from app.database import get_db
from app.models import Task
from app.services.task_schedule import (
    get_due_status,
    get_task_dates_for_month,
)
from app.services.weather import (
    get_weather_description,
    get_weather_forecast,
    get_weather_warnings,
)

BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter()

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


@router.get("/calendar", response_class=HTMLResponse)
async def calendar_page(
    request: Request,
    year: int | None = Query(default=None),
    month: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    today = date.today()

    weather_by_date = get_weather_forecast()

    for weather in weather_by_date.values():
        description = get_weather_description(
            weather.get("weather_code")
        )

        weather["label"] = description["label"]
        weather["icon"] = description["icon"]

        weather["warnings"] = get_weather_warnings(
            weather
        )

    if year is None:
        year = today.year

    if month is None:
        month = today.month

    # Ungültige Monate abfangen
    if month < 1 or month > 12:
        year = today.year
        month = today.month

    # Vorheriger Monat
    if month == 1:
        previous_year = year - 1
        previous_month = 12
    else:
        previous_year = year
        previous_month = month - 1

    # Nächster Monat
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1

    # Deutscher Monatsname
    month_names = [
        "",
        "Januar",
        "Februar",
        "März",
        "April",
        "Mai",
        "Juni",
        "Juli",
        "August",
        "September",
        "Oktober",
        "November",
        "Dezember",
    ]

    month_name = month_names[month]

    # Vollständige Kalenderwochen Montag bis Sonntag
    month_calendar = calendar.Calendar(
        firstweekday=calendar.MONDAY
    )

    weeks = month_calendar.monthdatescalendar(
        year,
        month,
    )

    # ----------------------------------------------
    # Aufgaben für den angezeigten Monat
    # ----------------------------------------------

    all_tasks = db.query(Task).all()

    tasks_by_date = {}
    task_status_by_date = {}

    for task in all_tasks:
        task_dates = get_task_dates_for_month(
            task,
            year=year,
            month=month,
            today=today,
        )

        for task_date in task_dates:
            tasks_by_date.setdefault(
                task_date,
                [],
            ).append(task)

            task_status_by_date[
                (task_date, task.id)
            ] = get_due_status(
                task_date,
                today=today,
            )

    # Aufgaben innerhalb eines Tages sortieren.
    # Hohe Priorität zuerst.
    priority_order = {
        "high": 0,
        "normal": 1,
        "low": 2,
    }

    for day_tasks in tasks_by_date.values():
        day_tasks.sort(
            key=lambda task: priority_order.get(
                task.priority,
                1,
            )
        )

    return templates.TemplateResponse(
        request=request,
        name="calendar.html",
        context={
            "page": "calendar",
            "app_name": APP_NAME,
            "version": APP_VERSION,
            "today": today,
            "year": year,
            "month": month,
            "month_name": month_name,
            "previous_year": previous_year,
            "previous_month": previous_month,
            "next_year": next_year,
            "next_month": next_month,
            "weeks": weeks,
            "tasks_by_date": tasks_by_date,
            "task_status_by_date": task_status_by_date,
            "weather_by_date": weather_by_date,
        },
    )

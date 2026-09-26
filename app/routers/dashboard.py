from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import APP_NAME, APP_VERSION
from app.database import get_db
from app.models.garden_area import GardenArea
from app.models.plant import Plant
from app.models.task import Task
from app.services.task_schedule import get_next_due_date
from app.services.weather import (
    get_weather_description,
    get_weather_forecast,
    get_weather_warnings,
)


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
):
    areas = db.query(GardenArea).all()
    plants = db.query(Plant).all()
    all_tasks = db.query(Task).all()

    open_task_count = 0

    for task in all_tasks:
        if task.execution_type == "once":
            if not task.completed:
                open_task_count += 1

        elif task.execution_type == "recurring":
            if get_next_due_date(task) is not None:
                open_task_count += 1

    today = date.today()

    weather_by_date = get_weather_forecast()
    weather_today = weather_by_date.get(today)

    if weather_today:
        description = get_weather_description(
            weather_today.get("weather_code")
        )

        weather_today["label"] = description["label"]
        weather_today["icon"] = description["icon"]
        weather_today["warnings"] = get_weather_warnings(
            weather_today
        )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "page": "dashboard",
            "app_name": APP_NAME,
            "version": APP_VERSION,
            "areas": areas,
            "plants": plants,
            "open_task_count": open_task_count,
            "weather_today": weather_today,
        },
    )

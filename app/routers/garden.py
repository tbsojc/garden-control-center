from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, selectinload

from app.config import APP_NAME, APP_VERSION
from app.database import get_db
from app.models import GardenArea, Task
from app.services.task_schedule import get_next_due_date


BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter()

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


# --------------------------------------------------
# Garten
# --------------------------------------------------

@router.get("/garden", response_class=HTMLResponse)
async def garden(
    request: Request,
    db: Session = Depends(get_db),
):
    areas = (
        db.query(GardenArea)
        .options(
            selectinload(GardenArea.plants)
        )
        .order_by(GardenArea.name)
        .all()
    )

    today = date.today()

    plant_ids = [
        plant.id
        for area in areas
        for plant in area.plants
    ]

    tasks_by_plant = {
        plant_id: []
        for plant_id in plant_ids
    }

    if plant_ids:
        plant_tasks = (
            db.query(Task)
            .filter(Task.plant_id.in_(plant_ids))
            .all()
        )

        for task in plant_tasks:
            due_date = get_next_due_date(
                task,
                today=today,
            )

            if due_date is None:
                continue

            days_until_due = (
                due_date - today
            ).days

            tasks_by_plant[task.plant_id].append({
                "task": task,
                "due_date": due_date,
                "days_until_due": days_until_due,
            })

    for task_items in tasks_by_plant.values():
        task_items.sort(
            key=lambda item: item["due_date"]
        )

    return templates.TemplateResponse(
        request=request,
        name="garden.html",
        context={
            "page": "garden",
            "app_name": APP_NAME,
            "version": APP_VERSION,
            "areas": areas,
            "tasks_by_plant": tasks_by_plant,
        },
    )

@router.post("/garden/areas")
async def create_garden_area(
    name: str = Form(...),
    area_type: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    area = GardenArea(
        name=name.strip(),
        area_type=area_type,
        description=description.strip() or None,
    )

    db.add(area)
    db.commit()

    return RedirectResponse("/garden", status_code=303)


@router.post("/garden/areas/{area_id}/delete")
async def delete_garden_area(
    area_id: int,
    db: Session = Depends(get_db),
):
    area = db.get(GardenArea, area_id)

    if area:
        db.delete(area)
        db.commit()

    return RedirectResponse("/garden", status_code=303)


@router.get(
    "/garden/areas/{area_id}/edit",
    response_class=HTMLResponse,
)
async def edit_garden_area_page(
    area_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    area = db.get(GardenArea, area_id)

    if area is None:
        return RedirectResponse(
            "/garden",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="edit_garden_area.html",
        context={
            "page": "edit_garden_area",
            "app_name": APP_NAME,
            "version": APP_VERSION,
            "area": area,
        },
    )


@router.post("/garden/areas/{area_id}/edit")
async def edit_garden_area(
    area_id: int,
    name: str = Form(...),
    area_type: str = Form(...),
    area_size: str = Form(""),
    light_condition: str = Form(""),
    soil_type: str = Form(""),
    soil_ph: str = Form(""),
    irrigation_zone: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    area = db.get(GardenArea, area_id)

    if area is None:
        return RedirectResponse(
            "/garden",
            status_code=303,
        )

    area.name = name.strip()
    area.area_type = area_type

    area.area_size = (
        float(area_size)
        if area_size
        else None
    )

    area.light_condition = (
        light_condition.strip()
        or None
    )

    area.soil_type = (
        soil_type.strip()
        or None
    )

    area.soil_ph = (
        float(soil_ph)
        if soil_ph
        else None
    )

    area.irrigation_zone = (
        irrigation_zone.strip()
        or None
    )

    area.description = (
        description.strip()
        or None
    )

    db.commit()

    return RedirectResponse(
        "/garden",
        status_code=303,
    )

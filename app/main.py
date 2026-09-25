from datetime import date, datetime
from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import CareRule, GardenArea, Plant, PlantSpecies, Task
from app.services.task_generator import generate_tasks

BASE_DIR = Path(__file__).resolve().parent


app = FastAPI(
    title="Garden Control Center",
    version="0.8.0",
)


app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------


def empty_string_to_int(value: str) -> int | None:
    if not value:
        return None

    return int(value)


# --------------------------------------------------
# Dashboard
# --------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
):
    areas = db.query(GardenArea).all()
    plants = db.query(Plant).all()
    species = db.query(PlantSpecies).all()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "page": "dashboard",
            "app_name": "Garden Control Center",
            "version": "0.5.0",
            "areas": areas,
            "plants": plants,
            "species": species,
        },
    )


# --------------------------------------------------
# Garten
# --------------------------------------------------


@app.get("/garden", response_class=HTMLResponse)
async def garden(
    request: Request,
    db: Session = Depends(get_db),
):
    areas = (
        db.query(GardenArea)
        .order_by(GardenArea.name)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "page": "garden",
            "app_name": "Garden Control Center",
            "version": "0.5.0",
            "areas": areas,
        },
    )


@app.post("/garden/areas")
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


@app.post("/garden/areas/{area_id}/delete")
async def delete_garden_area(
    area_id: int,
    db: Session = Depends(get_db),
):
    area = db.get(GardenArea, area_id)

    if area:
        db.delete(area)
        db.commit()

    return RedirectResponse("/garden", status_code=303)


# --------------------------------------------------
# Pflanzenwissen
# --------------------------------------------------


@app.get("/plant-library", response_class=HTMLResponse)
async def plant_library(
    request: Request,
    db: Session = Depends(get_db),
):
    species = (
        db.query(PlantSpecies)
        .order_by(PlantSpecies.name)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "page": "plant_library",
            "app_name": "Garden Control Center",
            "version": "0.5.0",
            "species": species,
        },
    )


@app.post("/plant-library")
async def create_species(
    name: str = Form(...),
    category: str = Form(...),
    sowing_start: str = Form(""),
    sowing_end: str = Form(""),
    planting_start: str = Form(""),
    planting_end: str = Form(""),
    harvest_start: str = Form(""),
    harvest_end: str = Form(""),
    water_need: str = Form("mittel"),
    nutrient_need: str = Form("mittel"),
    frost_sensitive: bool = Form(False),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    species = PlantSpecies(
        name=name.strip(),
        category=category,
        sowing_start=empty_string_to_int(sowing_start),
        sowing_end=empty_string_to_int(sowing_end),
        planting_start=empty_string_to_int(planting_start),
        planting_end=empty_string_to_int(planting_end),
        harvest_start=empty_string_to_int(harvest_start),
        harvest_end=empty_string_to_int(harvest_end),
        water_need=water_need,
        nutrient_need=nutrient_need,
        frost_sensitive=frost_sensitive,
        description=description.strip() or None,
    )

    db.add(species)
    db.commit()

    return RedirectResponse(
        "/plant-library",
        status_code=303,
    )


@app.post("/plant-library/{species_id}/delete")
async def delete_species(
    species_id: int,
    db: Session = Depends(get_db),
):
    species = db.get(PlantSpecies, species_id)

    if species and not species.plants:
        db.delete(species)
        db.commit()

    return RedirectResponse(
        "/plant-library",
        status_code=303,
    )

# --------------------------------------------------
# Pflegeregeln
# --------------------------------------------------


@app.get("/plant-library/{species_id}/rules", response_class=HTMLResponse)
async def care_rules(
    species_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    species = db.get(PlantSpecies, species_id)

    if not species:
        return RedirectResponse(
            "/plant-library",
            status_code=303,
        )

    rules = (
        db.query(CareRule)
        .filter(CareRule.species_id == species_id)
        .order_by(
            CareRule.start_month,
            CareRule.title,
        )
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "page": "care_rules",
            "app_name": "Garden Control Center",
            "version": "0.6.0",
            "species_item": species,
            "rules": rules,
        },
    )


@app.post("/plant-library/{species_id}/rules")
async def create_care_rule(
    species_id: int,
    title: str = Form(...),
    task_type: str = Form(...),
    start_month: int = Form(...),
    end_month: int = Form(...),
    interval_days: str = Form(""),
    priority: str = Form("normal"),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    species = db.get(PlantSpecies, species_id)

    if not species:
        return RedirectResponse(
            "/plant-library",
            status_code=303,
        )

    interval = None

    if interval_days:
        interval = max(1, int(interval_days))

    rule = CareRule(
        species_id=species_id,
        title=title.strip(),
        task_type=task_type,
        start_month=start_month,
        end_month=end_month,
        interval_days=interval,
        priority=priority,
        description=description.strip() or None,
    )

    db.add(rule)
    db.commit()

    return RedirectResponse(
        f"/plant-library/{species_id}/rules",
        status_code=303,
    )


@app.post("/care-rules/{rule_id}/delete")
async def delete_care_rule(
    rule_id: int,
    db: Session = Depends(get_db),
):
    rule = db.get(CareRule, rule_id)

    if not rule:
        return RedirectResponse(
            "/plant-library",
            status_code=303,
        )

    species_id = rule.species_id

    db.delete(rule)
    db.commit()

    return RedirectResponse(
        f"/plant-library/{species_id}/rules",
        status_code=303,
    )


# --------------------------------------------------
# Pflanzen
# --------------------------------------------------


@app.get("/plants", response_class=HTMLResponse)
async def plants(
    request: Request,
    db: Session = Depends(get_db),
):
    all_plants = (
        db.query(Plant)
        .order_by(Plant.name)
        .all()
    )

    areas = (
        db.query(GardenArea)
        .order_by(GardenArea.name)
        .all()
    )

    species = (
        db.query(PlantSpecies)
        .order_by(PlantSpecies.name)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "page": "plants",
            "app_name": "Garden Control Center",
            "version": "0.5.0",
            "plants": all_plants,
            "areas": areas,
            "species": species,
        },
    )


@app.post("/plants")
async def create_plant(
    name: str = Form(...),
    variety: str = Form(""),
    quantity: int = Form(1),
    planted_at: str = Form(""),
    garden_area_id: int = Form(...),
    species_id: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    plant_date = None

    if planted_at:
        plant_date = date.fromisoformat(planted_at)

    selected_species_id = None

    if species_id:
        selected_species_id = int(species_id)

    plant = Plant(
        name=name.strip(),
        variety=variety.strip() or None,
        quantity=max(1, quantity),
        planted_at=plant_date,
        garden_area_id=garden_area_id,
        species_id=selected_species_id,
        notes=notes.strip() or None,
    )

    db.add(plant)
    db.commit()

    return RedirectResponse("/plants", status_code=303)


@app.post("/plants/{plant_id}/delete")
async def delete_plant(
    plant_id: int,
    db: Session = Depends(get_db),
):
    plant = db.get(Plant, plant_id)

    if plant:
        db.delete(plant)
        db.commit()

    return RedirectResponse("/plants", status_code=303)


# --------------------------------------------------
# Aufgaben
# --------------------------------------------------


@app.get("/tasks", response_class=HTMLResponse)
async def tasks(
    request: Request,
    db: Session = Depends(get_db),
):
    all_tasks = (
        db.query(Task)
        .order_by(
            Task.completed,
            Task.due_date,
        )
        .all()
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
        name="index.html",
        context={
            "page": "tasks",
            "app_name": "Garden Control Center",
            "version": "0.7.0",
            "tasks": all_tasks,
            "areas": areas,
            "plants": plants,
            "today": date.today(),
        },
    )

@app.post("/tasks/generate")
async def generate_automatic_tasks(
    db: Session = Depends(get_db),
):
    generate_tasks(
        db=db,
        days=30,
    )

    return RedirectResponse(
        "/tasks",
        status_code=303,
    )

@app.post("/tasks")
async def create_task(
    title: str = Form(...),
    due_date: str = Form(...),
    priority: str = Form("normal"),
    garden_area_id: str = Form(""),
    plant_id: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    task = Task(
        title=title.strip(),
        due_date=date.fromisoformat(due_date),
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
        source="manual",
    )

    db.add(task)
    db.commit()

    return RedirectResponse(
        "/tasks",
        status_code=303,
    )


@app.post("/tasks/{task_id}/toggle")
async def toggle_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)

    if task:
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


@app.post("/tasks/{task_id}/delete")
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

# --------------------------------------------------
# API
# --------------------------------------------------


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "application": "Garden Control Center",
        "version": "0.5.0",
    }

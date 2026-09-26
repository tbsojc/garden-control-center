from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import APP_NAME, APP_VERSION
from app.database import get_db
from app.models import GardenArea, Plant, PlantSpecies
from app.services.location_analysis import analyze_location


BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter()

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


# --------------------------------------------------
# Pflanzen
# --------------------------------------------------


@router.get("/plants", response_class=HTMLResponse)
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
        name="plants.html",
        context={
            "page": "plants",
            "app_name": APP_NAME,
            "version": APP_VERSION,
            "plants": all_plants,
            "areas": areas,
            "species": species,
        },
    )


@router.post("/plants")
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

    return RedirectResponse(
        "/plants",
        status_code=303,
    )


@router.post("/plants/{plant_id}/delete")
async def delete_plant(
    plant_id: int,
    db: Session = Depends(get_db),
):
    plant = db.get(Plant, plant_id)

    if plant:
        db.delete(plant)
        db.commit()

    return RedirectResponse(
        "/plants",
        status_code=303,
    )


@router.get(
    "/plants/{plant_id}/analysis",
    response_class=HTMLResponse,
)
async def plant_location_analysis(
    plant_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    plant = db.get(Plant, plant_id)

    if plant is None:
        return RedirectResponse(
            "/plants",
            status_code=303,
        )

    analysis = None

    if plant.species and plant.garden_area:
        analysis = analyze_location(
            plant.species,
            plant.garden_area,
        )

    return templates.TemplateResponse(
        request=request,
        name="plant_analysis.html",
        context={
            "page": "plant_analysis",
            "app_name": APP_NAME,
            "version": APP_VERSION,
            "plant": plant,
            "analysis": analysis,
        },
    )

from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import APP_NAME, APP_VERSION
from app.database import get_db
from app.models import PlantSpecies


BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter()

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)

def parse_plant_species_data(
    name: str,
    category: str,
    sowing_start: str,
    sowing_end: str,
    planting_start: str,
    planting_end: str,
    harvest_start: str,
    harvest_end: str,
    water_need: str,
    nutrient_need: str,
    light_requirement: str,
    soil_type: str,
    soil_moisture_min: str,
    soil_moisture_max: str,
    soil_ph_min: str,
    soil_ph_max: str,
    frost_sensitive: str | None,
    waterlogging_sensitive: str | None,
    lime_sensitive: str | None,
    description: str,
):
    return {
        "name": name.strip(),
        "category": category.strip(),
        "sowing_start": (
            int(sowing_start)
            if sowing_start
            else None
        ),
        "sowing_end": (
            int(sowing_end)
            if sowing_end
            else None
        ),
        "planting_start": (
            int(planting_start)
            if planting_start
            else None
        ),
        "planting_end": (
            int(planting_end)
            if planting_end
            else None
        ),
        "harvest_start": (
            int(harvest_start)
            if harvest_start
            else None
        ),
        "harvest_end": (
            int(harvest_end)
            if harvest_end
            else None
        ),
        "water_need": water_need,
        "nutrient_need": nutrient_need,
        "light_requirement": (
            light_requirement.strip() or None
        ),
        "soil_type": (
            soil_type.strip() or None
        ),
        "soil_moisture_min": (
            float(soil_moisture_min)
            if soil_moisture_min
            else None
        ),
        "soil_moisture_max": (
            float(soil_moisture_max)
            if soil_moisture_max
            else None
        ),
        "soil_ph_min": (
            float(soil_ph_min)
            if soil_ph_min
            else None
        ),
        "soil_ph_max": (
            float(soil_ph_max)
            if soil_ph_max
            else None
        ),
        "frost_sensitive": (
            frost_sensitive is not None
        ),
        "waterlogging_sensitive": (
            waterlogging_sensitive is not None
        ),
        "lime_sensitive": (
            lime_sensitive is not None
        ),
        "description": (
            description.strip() or None
        ),
    }

# --------------------------------------------------
# Pflanzenwissen
# --------------------------------------------------


@router.get("/plant-library", response_class=HTMLResponse)
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
        name="plant_library.html",
        context={
            "page": "plant_library",
            "app_name": APP_NAME,
            "version": APP_VERSION,
            "species": species,
        },
    )


@router.post("/plant-library")
async def create_plant_species(
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

    light_requirement: str = Form(""),
    soil_type: str = Form(""),

    soil_moisture_min: str = Form(""),
    soil_moisture_max: str = Form(""),

    soil_ph_min: str = Form(""),
    soil_ph_max: str = Form(""),

    frost_sensitive: str | None = Form(None),
    waterlogging_sensitive: str | None = Form(None),
    lime_sensitive: str | None = Form(None),

    description: str = Form(""),

    db: Session = Depends(get_db),
):
    species_data = parse_plant_species_data(
        name=name,
        category=category,
        sowing_start=sowing_start,
        sowing_end=sowing_end,
        planting_start=planting_start,
        planting_end=planting_end,
        harvest_start=harvest_start,
        harvest_end=harvest_end,
        water_need=water_need,
        nutrient_need=nutrient_need,
        light_requirement=light_requirement,
        soil_type=soil_type,
        soil_moisture_min=soil_moisture_min,
        soil_moisture_max=soil_moisture_max,
        soil_ph_min=soil_ph_min,
        soil_ph_max=soil_ph_max,
        frost_sensitive=frost_sensitive,
        waterlogging_sensitive=waterlogging_sensitive,
        lime_sensitive=lime_sensitive,
        description=description,
    )

    species = PlantSpecies(**species_data)

    db.add(species)
    db.commit()

    return RedirectResponse(
        "/plant-library",
        status_code=303,
    )

    db.add(species)
    db.commit()

    return RedirectResponse(
        "/plant-library",
        status_code=303,
    )


@router.get(
    "/plant-library/{species_id}/edit",
    response_class=HTMLResponse,
)
async def edit_plant_species_page(
    species_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    species = db.get(PlantSpecies, species_id)

    if species is None:
        return RedirectResponse(
            "/plant-library",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="edit_plant_species.html",
        context={
            "page": "edit_plant_species",
            "app_name": APP_NAME,
            "version": APP_VERSION,
            "species": species,
        },
    )


@router.post("/plant-library/{species_id}/edit")
async def edit_plant_species(
    species_id: int,
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
    light_requirement: str = Form(""),
    soil_type: str = Form(""),
    soil_moisture_min: str = Form(""),
    soil_moisture_max: str = Form(""),
    soil_ph_min: str = Form(""),
    soil_ph_max: str = Form(""),
    frost_sensitive: str | None = Form(None),
    waterlogging_sensitive: str | None = Form(None),
    lime_sensitive: str | None = Form(None),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    species = db.get(PlantSpecies, species_id)

    if species is None:
        return RedirectResponse(
            "/plant-library",
            status_code=303,
        )

    species_data = parse_plant_species_data(
        name=name,
        category=category,
        sowing_start=sowing_start,
        sowing_end=sowing_end,
        planting_start=planting_start,
        planting_end=planting_end,
        harvest_start=harvest_start,
        harvest_end=harvest_end,
        water_need=water_need,
        nutrient_need=nutrient_need,
        light_requirement=light_requirement,
        soil_type=soil_type,
        soil_moisture_min=soil_moisture_min,
        soil_moisture_max=soil_moisture_max,
        soil_ph_min=soil_ph_min,
        soil_ph_max=soil_ph_max,
        frost_sensitive=frost_sensitive,
        waterlogging_sensitive=waterlogging_sensitive,
        lime_sensitive=lime_sensitive,
        description=description,
    )

    for field, value in species_data.items():
        setattr(species, field, value)

    db.commit()

    return RedirectResponse(
        "/plant-library",
        status_code=303,
    )

    species.description = (
        description.strip() or None
    )

    db.commit()

    return RedirectResponse(
        "/plant-library",
        status_code=303,
    )


@router.post("/plant-library/{species_id}/delete")
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

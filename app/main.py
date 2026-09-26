from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import APP_NAME, APP_VERSION
from app.routers import (
    calendar,
    dashboard,
    garden,
    plant_library,
    plants,
    tasks,
    weather
)


BASE_DIR = Path(__file__).resolve().parent


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
)


# --------------------------------------------------
# Router
# --------------------------------------------------

app.include_router(dashboard.router)
app.include_router(garden.router)
app.include_router(plants.router)
app.include_router(plant_library.router)
app.include_router(tasks.router)
app.include_router(calendar.router)
app.include_router(weather.router)

# --------------------------------------------------
# Static Files
# --------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


# --------------------------------------------------
# API
# --------------------------------------------------

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "version": APP_VERSION,
    }

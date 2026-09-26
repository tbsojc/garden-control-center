from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import (
    APP_NAME,
    APP_VERSION,
    GARDEN_LOCATION_NAME,
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


@router.get("/weather", response_class=HTMLResponse)
async def weather_page(
    request: Request,
):
    weather_by_date = get_weather_forecast()

    weather_days = []

    for weather_date, weather in weather_by_date.items():
        description = get_weather_description(
            weather.get("weather_code")
        )

        warnings = get_weather_warnings(
            weather
        )

        weather_days.append({
            "date": weather_date,
            "weather_code": weather.get("weather_code"),
            "label": description["label"],
            "icon": description["icon"],
            "temperature_min": weather.get("temperature_min"),
            "temperature_max": weather.get("temperature_max"),
            "precipitation": weather.get("precipitation"),
            "precipitation_probability": weather.get(
                "precipitation_probability"
            ),
            "warnings": warnings,
        })

    return templates.TemplateResponse(
        request=request,
        name="weather.html",
        context={
            "page": "weather",
            "app_name": APP_NAME,
            "version": APP_VERSION,
            "location_name": GARDEN_LOCATION_NAME,
            "weather_days": weather_days,
        },
    )

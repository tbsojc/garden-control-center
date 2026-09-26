from datetime import date, datetime, timedelta

import httpx

from app.config import (
    GARDEN_LATITUDE,
    GARDEN_LONGITUDE,
    GARDEN_TIMEZONE,
)


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_CACHE_TTL = timedelta(minutes=15)

_weather_cache: dict[date, dict] | None = None
_weather_cache_time: datetime | None = None

def get_weather_forecast(
    forecast_days: int = 16,
) -> dict[date, dict]:
    """
    Lädt die tägliche Wettervorhersage für den Garten.

    Die Wetterdaten werden für 15 Minuten im Speicher
    zwischengespeichert.

    Bei einem Fehler wird ein leeres Dictionary zurückgegeben,
    damit andere Bereiche der Anwendung weiter funktionieren.
    """
    global _weather_cache
    global _weather_cache_time

    now = datetime.now()

    if (
        _weather_cache is not None
        and _weather_cache_time is not None
        and now - _weather_cache_time < WEATHER_CACHE_TTL
    ):
        return _weather_cache

    params = {
        "latitude": GARDEN_LATITUDE,
        "longitude": GARDEN_LONGITUDE,
        "timezone": GARDEN_TIMEZONE,
        "forecast_days": forecast_days,
        "daily": ",".join([
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
        ]),
    }

    try:
        response = httpx.get(
            OPEN_METEO_URL,
            params=params,
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
    except (
        httpx.HTTPError,
        ValueError,
    ):
        return {}

    daily = data.get("daily")

    if not daily:
        return {}

    dates = daily.get("time", [])
    weather_by_date = {}

    for index, date_string in enumerate(dates):
        try:
            forecast_date = date.fromisoformat(date_string)

            weather_by_date[forecast_date] = {
                "weather_code": daily["weather_code"][index],
                "temperature_max": daily[
                    "temperature_2m_max"
                ][index],
                "temperature_min": daily[
                    "temperature_2m_min"
                ][index],
                "precipitation": daily[
                    "precipitation_sum"
                ][index],
                "precipitation_probability": daily[
                    "precipitation_probability_max"
                ][index],
            }

        except (
            ValueError,
            KeyError,
            IndexError,
            TypeError,
        ):
            continue

    _weather_cache = weather_by_date
    _weather_cache_time = now

    return weather_by_date

def get_weather_description(
    weather_code: int | None,
) -> dict:
    """
    Übersetzt einen Open-Meteo-Wettercode
    in eine kurze Beschreibung und ein Symbol.
    """

    if weather_code == 0:
        return {
            "label": "Klar",
            "icon": "☀️",
        }

    if weather_code in (1, 2):
        return {
            "label": "Leicht bewölkt",
            "icon": "🌤️",
        }

    if weather_code == 3:
        return {
            "label": "Bewölkt",
            "icon": "☁️",
        }

    if weather_code in (45, 48):
        return {
            "label": "Nebel",
            "icon": "🌫️",
        }

    if weather_code in (51, 53, 55):
        return {
            "label": "Nieselregen",
            "icon": "🌦️",
        }

    if weather_code in (56, 57):
        return {
            "label": "Gefrierender Nieselregen",
            "icon": "🌧️",
        }

    if weather_code in (61, 63, 65):
        return {
            "label": "Regen",
            "icon": "🌧️",
        }

    if weather_code in (66, 67):
        return {
            "label": "Gefrierender Regen",
            "icon": "🌧️",
        }

    if weather_code in (71, 73, 75, 77):
        return {
            "label": "Schnee",
            "icon": "🌨️",
        }

    if weather_code in (80, 81, 82):
        return {
            "label": "Regenschauer",
            "icon": "🌦️",
        }

    if weather_code in (85, 86):
        return {
            "label": "Schneeschauer",
            "icon": "🌨️",
        }

    if weather_code in (95, 96, 99):
        return {
            "label": "Gewitter",
            "icon": "⛈️",
        }

    return {
        "label": "Unbekannt",
        "icon": "❔",
    }

def get_weather_warnings(
    weather: dict,
) -> list[dict]:
    """
    Ermittelt Warnungen aus den Wetterdaten eines Tages.
    """

    warnings = []

    temperature_min = weather.get("temperature_min")

    if temperature_min is not None:
        if temperature_min <= 0:
            warnings.append({
                "type": "frost",
                "level": "danger",
                "label": "Frost",
                "icon": "❄️",
            })

        elif temperature_min <= 3:
            warnings.append({
                "type": "frost",
                "level": "warning",
                "label": "Frostgefahr",
                "icon": "⚠️",
            })

    return warnings

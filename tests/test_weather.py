from datetime import date
import httpx

from app.services.weather import (
    get_weather_description,
    get_weather_forecast,
    get_weather_warnings,
)

def test_weather_description_clear():
    result = get_weather_description(0)

    assert result["label"] == "Klar"
    assert result["icon"] == "☀️"


def test_weather_description_cloudy():
    result = get_weather_description(3)

    assert result["label"] == "Bewölkt"
    assert result["icon"] == "☁️"


def test_weather_description_rain():
    result = get_weather_description(61)

    assert result["label"] == "Regen"
    assert result["icon"] == "🌧️"


def test_weather_description_thunderstorm():
    result = get_weather_description(95)

    assert result["label"] == "Gewitter"
    assert result["icon"] == "⛈️"


def test_weather_description_unknown():
    result = get_weather_description(999)

    assert result["label"] == "Unbekannt"
    assert result["icon"] == "❔"


def test_weather_description_none():
    result = get_weather_description(None)

    assert result["label"] == "Unbekannt"
    assert result["icon"] == "❔"

def test_weather_forecast_returns_empty_dict_on_http_error(
    monkeypatch,
):
    def mock_get(*args, **kwargs):
        raise httpx.ConnectError(
            "Open-Meteo nicht erreichbar"
        )

    monkeypatch.setattr(
        "app.services.weather.httpx.get",
        mock_get,
    )

    result = get_weather_forecast()

    assert result == {}


def test_weather_forecast_parses_api_response(
    monkeypatch,
):
    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "daily": {
                    "time": [
                        "2026-09-26",
                        "2026-09-27",
                    ],
                    "weather_code": [
                        3,
                        61,
                    ],
                    "temperature_2m_max": [
                        19.4,
                        18.1,
                    ],
                    "temperature_2m_min": [
                        7.6,
                        14.1,
                    ],
                    "precipitation_sum": [
                        0.0,
                        8.55,
                    ],
                    "precipitation_probability_max": [
                        0,
                        42,
                    ],
                }
            }

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        "app.services.weather.httpx.get",
        mock_get,
    )

    result = get_weather_forecast()

    assert len(result) == 2

    assert result[date(2026, 9, 26)] == {
        "weather_code": 3,
        "temperature_max": 19.4,
        "temperature_min": 7.6,
        "precipitation": 0.0,
        "precipitation_probability": 0,
    }

    assert result[date(2026, 9, 27)] == {
        "weather_code": 61,
        "temperature_max": 18.1,
        "temperature_min": 14.1,
        "precipitation": 8.55,
        "precipitation_probability": 42,
    }

def test_weather_warning_no_frost():
    weather = {
        "temperature_min": 7.5,
    }

    assert get_weather_warnings(weather) == []


def test_weather_warning_frost_risk():
    weather = {
        "temperature_min": 2.0,
    }

    result = get_weather_warnings(weather)

    assert len(result) == 1
    assert result[0]["type"] == "frost"
    assert result[0]["level"] == "warning"
    assert result[0]["label"] == "Frostgefahr"


def test_weather_warning_frost():
    weather = {
        "temperature_min": -1.5,
    }

    result = get_weather_warnings(weather)

    assert len(result) == 1
    assert result[0]["type"] == "frost"
    assert result[0]["level"] == "danger"
    assert result[0]["label"] == "Frost"


def test_weather_warning_without_temperature():
    weather = {
        "temperature_min": None,
    }

    assert get_weather_warnings(weather) == []

def test_weather_forecast_uses_cache(
    monkeypatch,
):
    import app.services.weather as weather_service

    weather_service._weather_cache = None
    weather_service._weather_cache_time = None

    call_count = 0

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "daily": {
                    "time": ["2026-09-26"],
                    "weather_code": [3],
                    "temperature_2m_max": [19.4],
                    "temperature_2m_min": [7.6],
                    "precipitation_sum": [0.0],
                    "precipitation_probability_max": [0],
                }
            }

    def mock_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return MockResponse()

    monkeypatch.setattr(
        "app.services.weather.httpx.get",
        mock_get,
    )

    first_result = get_weather_forecast()
    second_result = get_weather_forecast()

    assert first_result == second_result
    assert call_count == 1

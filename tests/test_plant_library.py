from app.routers.plant_library import parse_plant_species_data


def test_parse_plant_species_complete_data():
    data = parse_plant_species_data(
        name="  Tomate  ",
        category="  Gemüse  ",
        sowing_start="2",
        sowing_end="4",
        planting_start="5",
        planting_end="6",
        harvest_start="7",
        harvest_end="10",
        water_need="hoch",
        nutrient_need="hoch",
        light_requirement="  sonnig  ",
        soil_type="  humos  ",
        soil_moisture_min="40.5",
        soil_moisture_max="70.5",
        soil_ph_min="5.5",
        soil_ph_max="7.0",
        frost_sensitive="on",
        waterlogging_sensitive="on",
        lime_sensitive="on",
        description="  Testbeschreibung  ",
    )

    assert data["name"] == "Tomate"
    assert data["category"] == "Gemüse"

    assert data["sowing_start"] == 2
    assert data["sowing_end"] == 4
    assert data["planting_start"] == 5
    assert data["planting_end"] == 6
    assert data["harvest_start"] == 7
    assert data["harvest_end"] == 10

    assert data["water_need"] == "hoch"
    assert data["nutrient_need"] == "hoch"

    assert data["light_requirement"] == "sonnig"
    assert data["soil_type"] == "humos"

    assert data["soil_moisture_min"] == 40.5
    assert data["soil_moisture_max"] == 70.5
    assert data["soil_ph_min"] == 5.5
    assert data["soil_ph_max"] == 7.0

    assert data["frost_sensitive"] is True
    assert data["waterlogging_sensitive"] is True
    assert data["lime_sensitive"] is True

    assert data["description"] == "Testbeschreibung"


def test_parse_plant_species_optional_fields_empty():
    data = parse_plant_species_data(
        name="Apfel",
        category="Obst",
        sowing_start="",
        sowing_end="",
        planting_start="",
        planting_end="",
        harvest_start="",
        harvest_end="",
        water_need="mittel",
        nutrient_need="mittel",
        light_requirement="",
        soil_type="",
        soil_moisture_min="",
        soil_moisture_max="",
        soil_ph_min="",
        soil_ph_max="",
        frost_sensitive=None,
        waterlogging_sensitive=None,
        lime_sensitive=None,
        description="",
    )

    assert data["name"] == "Apfel"
    assert data["category"] == "Obst"

    assert data["sowing_start"] is None
    assert data["sowing_end"] is None
    assert data["planting_start"] is None
    assert data["planting_end"] is None
    assert data["harvest_start"] is None
    assert data["harvest_end"] is None

    assert data["light_requirement"] is None
    assert data["soil_type"] is None

    assert data["soil_moisture_min"] is None
    assert data["soil_moisture_max"] is None
    assert data["soil_ph_min"] is None
    assert data["soil_ph_max"] is None

    assert data["frost_sensitive"] is False
    assert data["waterlogging_sensitive"] is False
    assert data["lime_sensitive"] is False

    assert data["description"] is None


def test_parse_plant_species_zero_values_are_valid():
    data = parse_plant_species_data(
        name="Testpflanze",
        category="Test",
        sowing_start="1",
        sowing_end="12",
        planting_start="1",
        planting_end="12",
        harvest_start="1",
        harvest_end="12",
        water_need="niedrig",
        nutrient_need="niedrig",
        light_requirement="sonnig",
        soil_type="sandig",
        soil_moisture_min="0",
        soil_moisture_max="100",
        soil_ph_min="0",
        soil_ph_max="14",
        frost_sensitive=None,
        waterlogging_sensitive=None,
        lime_sensitive=None,
        description="Test",
    )

    assert data["soil_moisture_min"] == 0.0
    assert data["soil_moisture_max"] == 100.0
    assert data["soil_ph_min"] == 0.0
    assert data["soil_ph_max"] == 14.0

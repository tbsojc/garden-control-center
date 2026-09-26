from app.models.garden_area import GardenArea
from app.models.plant_species import PlantSpecies


LIGHT_LEVELS = {
    "schattig": 1,
    "halbschattig_schattig": 2,
    "halbschattig": 3,
    "sonnig_halbschattig": 4,
    "sonnig": 5,
}


def analyze_location(
    species: PlantSpecies,
    area: GardenArea,
) -> dict:
    """
    Vergleicht die Standortanforderungen einer Pflanzenart
    mit den Eigenschaften eines Gartenbereichs.
    """

    results = []

    # -------------------------------------------------
    # Licht
    # -------------------------------------------------

    if species.light_requirement and area.light_condition:
        required_light = LIGHT_LEVELS.get(
            species.light_requirement
        )

        actual_light = LIGHT_LEVELS.get(
            area.light_condition
        )

        if required_light is not None and actual_light is not None:
            difference = abs(required_light - actual_light)

            if difference == 0:
                results.append({
                    "type": "light",
                    "status": "good",
                    "title": "Licht",
                    "message": "Die Lichtverhältnisse passen.",
                })

            elif difference == 1:
                results.append({
                    "type": "light",
                    "status": "warning",
                    "title": "Licht",
                    "message": (
                        "Die Lichtverhältnisse weichen leicht "
                        "von der Empfehlung ab."
                    ),
                })

            else:
                results.append({
                    "type": "light",
                    "status": "bad",
                    "title": "Licht",
                    "message": (
                        "Die Lichtverhältnisse passen nicht gut "
                        "zur Pflanzenart."
                    ),
                })

        else:
            results.append({
                "type": "light",
                "status": "unknown",
                "title": "Licht",
                "message": "Lichtdaten konnten nicht ausgewertet werden.",
            })

    else:
        results.append({
            "type": "light",
            "status": "unknown",
            "title": "Licht",
            "message": "Noch nicht genügend Lichtdaten vorhanden.",
        })

    # -------------------------------------------------
    # Boden-pH
    # -------------------------------------------------

    if (
        species.soil_ph_min is not None
        and species.soil_ph_max is not None
        and area.soil_ph is not None
    ):
        if species.soil_ph_min <= area.soil_ph <= species.soil_ph_max:
            results.append({
                "type": "ph",
                "status": "good",
                "title": "Boden-pH",
                "message": (
                    f"pH {area.soil_ph:.1f} liegt im Sollbereich "
                    f"{species.soil_ph_min:.1f}–"
                    f"{species.soil_ph_max:.1f}."
                ),
            })

        elif area.soil_ph < species.soil_ph_min:
            results.append({
                "type": "ph",
                "status": "warning",
                "title": "Boden-pH",
                "message": (
                    f"pH {area.soil_ph:.1f} ist zu niedrig. "
                    f"Sollbereich: {species.soil_ph_min:.1f}–"
                    f"{species.soil_ph_max:.1f}."
                ),
            })

        else:
            results.append({
                "type": "ph",
                "status": "warning",
                "title": "Boden-pH",
                "message": (
                    f"pH {area.soil_ph:.1f} ist zu hoch. "
                    f"Sollbereich: {species.soil_ph_min:.1f}–"
                    f"{species.soil_ph_max:.1f}."
                ),
            })

    else:
        results.append({
            "type": "ph",
            "status": "unknown",
            "title": "Boden-pH",
            "message": "Noch nicht genügend pH-Daten vorhanden.",
        })

    # -------------------------------------------------
    # Bodenfeuchtigkeit
    # -------------------------------------------------

    if (
        species.soil_moisture_min is not None
        and species.soil_moisture_max is not None
    ):
        results.append({
            "type": "moisture",
            "status": "unknown",
            "title": "Bodenfeuchtigkeit",
            "message": (
                f"Sollbereich: {species.soil_moisture_min:.1f}–"
                f"{species.soil_moisture_max:.1f} %. "
                "Noch kein Sensorwert vorhanden."
            ),
        })

    else:
        results.append({
            "type": "moisture",
            "status": "unknown",
            "title": "Bodenfeuchtigkeit",
            "message": (
                "Für diese Pflanzenart ist noch kein "
                "Feuchtigkeitsbereich hinterlegt."
            ),
        })

    return {
        "results": results,
    }

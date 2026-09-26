from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


if TYPE_CHECKING:
    from app.models.care_rule import CareRule
    from app.models.plant import Plant


class PlantSpecies(Base):
    __tablename__ = "plant_species"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # -------------------------------------------------
    # Saisonale Daten
    # -------------------------------------------------

    sowing_start: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    sowing_end: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    planting_start: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    planting_end: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    harvest_start: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    harvest_end: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # -------------------------------------------------
    # Allgemeiner Pflegebedarf
    # -------------------------------------------------

    water_need: Mapped[str] = mapped_column(
        String(20),
        default="mittel",
        nullable=False,
    )

    nutrient_need: Mapped[str] = mapped_column(
        String(20),
        default="mittel",
        nullable=False,
    )

    # -------------------------------------------------
    # Standortanforderungen
    # -------------------------------------------------

    light_requirement: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    soil_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # -------------------------------------------------
    # Bodenfeuchtigkeit
    #
    # Werte in Prozent.
    # Diese Werte sind später Sollwerte für Sensorik
    # und Bewässerungsentscheidungen.
    # -------------------------------------------------

    soil_moisture_min: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    soil_moisture_max: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # -------------------------------------------------
    # pH-Anforderungen
    # -------------------------------------------------

    soil_ph_min: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    soil_ph_max: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # -------------------------------------------------
    # Empfindlichkeiten
    # -------------------------------------------------

    frost_sensitive: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    waterlogging_sensitive: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    lime_sensitive: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # -------------------------------------------------
    # Beschreibung
    # -------------------------------------------------

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )

    # -------------------------------------------------
    # Beziehungen
    # -------------------------------------------------

    plants: Mapped[list["Plant"]] = relationship(
        back_populates="species",
    )

    care_rules: Mapped[list["CareRule"]] = relationship(
        back_populates="species",
    )

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


if TYPE_CHECKING:
    from app.models.plant import Plant
    from app.models.care_rule import CareRule


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

    water_need: Mapped[str] = mapped_column(
        String(20),
        default="mittel",
    )

    nutrient_need: Mapped[str] = mapped_column(
        String(20),
        default="mittel",
    )

    frost_sensitive: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )

    plants: Mapped[list["Plant"]] = relationship(
        back_populates="species",
    )

    care_rules: Mapped[list["CareRule"]] = relationship(
        back_populates="species",
        cascade="all, delete-orphan",
    )

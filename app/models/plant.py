from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


if TYPE_CHECKING:
    from app.models.garden_area import GardenArea
    from app.models.plant_species import PlantSpecies


class Plant(Base):
    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    variety: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    planted_at: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    garden_area_id: Mapped[int] = mapped_column(
        ForeignKey("garden_areas.id"),
        nullable=False,
    )

    species_id: Mapped[int | None] = mapped_column(
        ForeignKey("plant_species.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )

    garden_area: Mapped["GardenArea"] = relationship(
        back_populates="plants",
    )

    species: Mapped["PlantSpecies | None"] = relationship(
        back_populates="plants",
    )

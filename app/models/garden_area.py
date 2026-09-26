from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


if TYPE_CHECKING:
    from app.models.plant import Plant


class GardenArea(Base):
    __tablename__ = "garden_areas"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    area_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # -------------------------------------------------
    # Standortdaten
    # -------------------------------------------------

    area_size: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    light_condition: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    soil_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    soil_ph: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    irrigation_zone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
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

    plants: Mapped[list["Plant"]] = relationship(
        back_populates="garden_area",
        cascade="all, delete-orphan",
    )

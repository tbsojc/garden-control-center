from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


if TYPE_CHECKING:
    from app.models.plant_species import PlantSpecies


class CareRule(Base):
    __tablename__ = "care_rules"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    species_id: Mapped[int] = mapped_column(
        ForeignKey("plant_species.id"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    task_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    start_month: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    end_month: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    interval_days: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        default="normal",
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )

    species: Mapped["PlantSpecies"] = relationship(
        back_populates="care_rules",
    )

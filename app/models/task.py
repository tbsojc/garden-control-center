from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


if TYPE_CHECKING:
    from app.models.garden_area import GardenArea
    from app.models.plant import Plant
    from app.models.care_rule import CareRule


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        default="normal",
        nullable=False,
    )

    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(20),
        default="manual",
        nullable=False,
    )

    garden_area_id: Mapped[int | None] = mapped_column(
        ForeignKey("garden_areas.id"),
        nullable=True,
    )

    plant_id: Mapped[int | None] = mapped_column(
        ForeignKey("plants.id"),
        nullable=True,
    )

    care_rule_id: Mapped[int | None] = mapped_column(
        ForeignKey("care_rules.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )

    garden_area: Mapped["GardenArea | None"] = relationship()

    plant: Mapped["Plant | None"] = relationship()

    care_rule: Mapped["CareRule | None"] = relationship()

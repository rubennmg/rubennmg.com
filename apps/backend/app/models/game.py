from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Game(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "games"

    slug: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ranking_strategy: Mapped[str] = mapped_column(String(100), nullable=False)
    min_players: Mapped[int] = mapped_column(Integer, nullable=False)

    matches: Mapped[list["Match"]] = relationship(back_populates="game")

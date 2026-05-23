from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Player(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "players"

    display_name: Mapped[str] = mapped_column(
        String(150), unique=True, index=True, nullable=False
    )
    nickname: Mapped[str | None] = mapped_column(String(150), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    results: Mapped[list["MatchResult"]] = relationship(back_populates="player")

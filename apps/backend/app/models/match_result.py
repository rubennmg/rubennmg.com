import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MatchResult(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "match_results"
    __table_args__ = (
        UniqueConstraint(
            "match_id", "player_id", name="uq_match_results_match_id_player_id"
        ),
        CheckConstraint("score >= 0", name="ck_match_results_score_non_negative"),
    )

    match_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("matches.id"), nullable=False, index=True
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("players.id"), nullable=False, index=True
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_winner: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    match: Mapped["Match"] = relationship(back_populates="results")
    player: Mapped["Player"] = relationship(back_populates="results")

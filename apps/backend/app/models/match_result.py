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
    catan: Mapped["CatanResult | None"] = relationship(
        back_populates="result", cascade="all, delete-orphan", single_parent=True,
    )


class CatanResult(Base):
    __tablename__ = "catan_results"
    __table_args__ = tuple(
        CheckConstraint(f"{field} >= 0", name=f"ck_catan_results_{field}")
        for field in ("cities", "settlements", "roads", "victory_point_cards")
    )

    result_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("match_results.id", ondelete="CASCADE"), primary_key=True,
    )
    cities: Mapped[int | None] = mapped_column(Integer, nullable=True)
    settlements: Mapped[int | None] = mapped_column(Integer, nullable=True)
    roads: Mapped[int | None] = mapped_column(Integer, nullable=True)
    longest_road: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    largest_army: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    victory_point_cards: Mapped[int | None] = mapped_column(Integer, nullable=True)
    result: Mapped["MatchResult"] = relationship(back_populates="catan")

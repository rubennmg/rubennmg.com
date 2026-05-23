"""create board games schema

Revision ID: 202605230001
Revises:
Create Date: 2026-05-23 00:01:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "202605230001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "games",
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("display_name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("ranking_strategy", sa.String(length=100), nullable=False),
        sa.Column("min_players", sa.Integer(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_games_slug"), "games", ["slug"], unique=True)

    op.create_table(
        "players",
        sa.Column("display_name", sa.String(length=150), nullable=False),
        sa.Column("nickname", sa.String(length=150), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_players_display_name"), "players", ["display_name"], unique=True)

    op.create_table(
        "matches",
        sa.Column("game_id", sa.Uuid(), nullable=False),
        sa.Column("played_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_matches_game_id"), "matches", ["game_id"], unique=False)

    op.create_table(
        "match_results",
        sa.Column("match_id", sa.Uuid(), nullable=False),
        sa.Column("player_id", sa.Uuid(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("is_winner", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("score >= 0", name="ck_match_results_score_non_negative"),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", "player_id", name="uq_match_results_match_id_player_id"),
    )
    op.create_index(op.f("ix_match_results_match_id"), "match_results", ["match_id"], unique=False)
    op.create_index(op.f("ix_match_results_player_id"), "match_results", ["player_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_match_results_player_id"), table_name="match_results")
    op.drop_index(op.f("ix_match_results_match_id"), table_name="match_results")
    op.drop_table("match_results")
    op.drop_index(op.f("ix_matches_game_id"), table_name="matches")
    op.drop_table("matches")
    op.drop_index(op.f("ix_players_display_name"), table_name="players")
    op.drop_table("players")
    op.drop_index(op.f("ix_games_slug"), table_name="games")
    op.drop_table("games")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")

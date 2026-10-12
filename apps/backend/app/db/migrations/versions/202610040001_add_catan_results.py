"""Add optional Catán details without changing existing results."""

from alembic import op
import sqlalchemy as sa

revision = "202610040001"
down_revision = "202605230001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "catan_results",
        sa.Column("result_id", sa.Uuid(), nullable=False),
        sa.Column("cities", sa.Integer(), nullable=True),
        sa.Column("settlements", sa.Integer(), nullable=True),
        sa.Column("roads", sa.Integer(), nullable=True),
        sa.Column("longest_road", sa.Boolean(), nullable=True),
        sa.Column("largest_army", sa.Boolean(), nullable=True),
        sa.Column("victory_point_cards", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["result_id"], ["match_results.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("result_id"),
        *(sa.CheckConstraint(f"{field} >= 0", name=f"ck_catan_results_{field}")
          for field in ("cities", "settlements", "roads", "victory_point_cards")),
    )


def downgrade() -> None:
    op.drop_table("catan_results")

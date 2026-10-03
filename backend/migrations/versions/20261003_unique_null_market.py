"""ensure one commodity per code with a null market

Revision ID: 20261003_unique_null_market
Revises: 20260425_income_revenue_nullable
Create Date: 2026-10-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20261003_unique_null_market"
down_revision = "20260425_income_revenue_nullable"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "uq_commodities_code_null_market",
        "mst_commodities",
        ["code"],
        unique=True,
        postgresql_where=sa.text("market IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_commodities_code_null_market", table_name="mst_commodities")
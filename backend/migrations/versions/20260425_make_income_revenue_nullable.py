"""make income.revenue nullable

Revision ID: 20260425_make_income_revenue_nullable
Revises: f892bf659b0c
Create Date: 2026-04-25 05:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260425_make_income_revenue_nullable'
down_revision = 'f892bf659b0c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'trn_income_stmt',
        'revenue',
        existing_type=sa.Float(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'trn_income_stmt',
        'revenue',
        existing_type=sa.Float(),
        nullable=False,
    )

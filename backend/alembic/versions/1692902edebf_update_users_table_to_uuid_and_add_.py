"""Update users table to UUID and add missing columns

Revision ID: 1692902edebf
Revises: 6e7ad66a2f10
Create Date: 2025-08-12 03:11:51.290111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1692902edebf'
down_revision: Union[str, None] = '6e7ad66a2f10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

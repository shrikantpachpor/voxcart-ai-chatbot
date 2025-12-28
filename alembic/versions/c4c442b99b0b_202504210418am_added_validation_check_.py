"""202504210418am: added validation check on orderhistory model

Revision ID: c4c442b99b0b
Revises: 75ffed2fe71e
Create Date: 2025-04-21 04:18:35.196823

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4c442b99b0b'
down_revision: Union[str, None] = '75ffed2fe71e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

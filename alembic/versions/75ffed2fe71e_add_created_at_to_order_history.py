"""add_created_at_to_order_history

Revision ID: 75ffed2fe71e
Revises: 938949a63ba8
Create Date: 2025-04-21 04:01:13.356704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75ffed2fe71e'
down_revision: Union[str, None] = '938949a63ba8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('order_history', 
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False)
    )
    op.add_column('order_history', 
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False)
    )

def downgrade():
    op.drop_column('order_history', 'created_at')
    op.drop_column('order_history', 'updated_at')

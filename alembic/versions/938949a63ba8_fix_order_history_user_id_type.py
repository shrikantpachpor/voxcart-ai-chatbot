"""fix order_history user_id type

Revision ID: 938949a63ba8
Revises: 5b6da9b8f465
Create Date: 2025-04-21 03:06:55.516855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '938949a63ba8'
down_revision: Union[str, None] = '5b6da9b8f465'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Step 1: Drop existing foreign key if it exists
    op.execute('ALTER TABLE order_history DROP CONSTRAINT IF EXISTS order_history_user_id_fkey')
    
    # Step 2: Convert column type
    op.alter_column('order_history', 'user_id',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               postgresql_using='user_id::integer')
    
    # Step 3: Recreate foreign key
    op.create_foreign_key(
        'order_history_user_id_fkey',
        'order_history', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    # Reverse the changes
    op.drop_constraint('order_history_user_id_fkey', 'order_history', type_='foreignkey')
    op.alter_column('order_history', 'user_id',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR())
"""Add is_staff field to User model

Revision ID: 6ec04a33369d
Revises: 8e825dae1884
Create Date: 2025-08-04 13:50:17.259425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ec04a33369d'
down_revision: Union[str, Sequence[str], None] = '8e825dae1884'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if column exists before adding
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'is_staff' not in columns:
        op.add_column('users', sa.Column('is_staff', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    """Downgrade schema."""
    # Check if column exists before dropping
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'is_staff' in columns:
        op.drop_column('users', 'is_staff')

"""merge_heads

Revision ID: 714ef079d138
Revises: 6ec04a33369d, fca21b76a184
Create Date: 2025-08-05 09:06:25.716084

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '714ef079d138'
down_revision: Union[str, Sequence[str], None] = ('6ec04a33369d', 'fca21b76a184')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

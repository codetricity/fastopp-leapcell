"""add_photo_url_to_webinar_registrants

Revision ID: fca21b76a184
Revises: 8e825dae1884
Create Date: 2025-08-05 09:05:23.188399

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fca21b76a184'
down_revision: Union[str, Sequence[str], None] = '8e825dae1884'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('webinar_registrants', sa.Column('photo_url', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('webinar_registrants', 'photo_url')

"""create_enums

Revision ID: cf9857c61471
Revises:
Create Date: 2023-06-21 20:14:40.886402

"""
from alembic import op

from app.models.enums import PgCipherType

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Enums are created automatically when they are used in a table.
    This is a workaround to create them manually.
    """
    pass

def downgrade() -> None:
    """
    Drop enums:
        - PgCipherType
    """
    PgCipherType.drop(op.get_bind(), checkfirst=True)

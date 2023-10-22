"""create_cipher

Revision ID: 0005
Revises: 0004
Create Date: 2023-10-03 22:51:12.404481

"""
import sqlalchemy as sa
from alembic import op

from app.models.enums import PgCipherType

# revision identifiers, used by Alembic.
revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """ Create cipher table """
    op.create_table(
        "cipher",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("collection_id", sa.UUID(), nullable=True),
        sa.Column("type", PgCipherType, nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["collection_id"], ["collection.id"], name=op.f("fk_cipher_collection_id_collection")),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name=op.f("fk_cipher_user_id_user")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cipher")),
    )
    op.create_index(op.f("ix_cipher_user_id"), "cipher", ["user_id"], unique=False)
    op.create_index(op.f("ix_cipher_collection_id"), "cipher", ["collection_id"], unique=False)

def downgrade() -> None:
    """ Drop cipher table """
    op.drop_index(op.f("ix_cipher_user_id"), table_name="cipher")
    op.drop_index(op.f("ix_cipher_collection_id"), table_name="cipher")
    op.drop_table("cipher")

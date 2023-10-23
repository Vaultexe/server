"""create_cipher

Revision ID: 0004
Revises: 0003
Create Date: 2023-10-03 22:32:44.951197

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create collection table"""
    op.create_table(
        "collection",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name=op.f("fk_collection_user_id_user")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_collection")),
    )
    op.create_index(op.f("ix_collection_user_id"), "collection", ["user_id"], unique=False)
    op.create_unique_constraint(op.f("uix_collection_user_id_name"), "collection", ["user_id", "name"])

def downgrade() -> None:
    """Drop collection table table"""
    op.drop_constraint(op.f("uix_collection_user_id_name"), table_name="collection", type_="unique")
    op.drop_index(op.f("ix_collection_user_id"), table_name="collection")
    op.drop_table("collection")

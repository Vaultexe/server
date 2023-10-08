"""create_device

Revision ID: 0002
Revises: 0001
Create Date: 2023-09-29 00:51:51.741909

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """ Create device table """
    op.create_table(
        "device",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("user_agent", sa.String(length=350), nullable=False),
        sa.Column("regestered_at",sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_login_ip", sa.String(length=45), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name=op.f("fk_device_user_id_user")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_device")),
    )
    op.create_index(op.f("ix_device_id"), "device", ["id"], unique=False)
    op.create_index(op.f("ix_device_user_id"), "device", ["user_id"], unique=False)


def downgrade() -> None:
    """ Drop device table """
    op.drop_index(op.f("ix_device_user_id"), table_name="device")
    op.drop_index(op.f("ix_device_id"), table_name="device")
    op.drop_table("device")

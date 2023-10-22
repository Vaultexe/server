"""create_invitation

Revision ID: 0006
Revises: 0005
Create Date: 2023-10-16 23:27:06.086641

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create invitation table"""
    op.create_table(
        "invitation",
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("invitee_id", sa.UUID(), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_valid", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["user.id"], name=op.f("fk_invitation_created_by_user")),
        sa.ForeignKeyConstraint(["invitee_id"], ["user.id"], name=op.f("fk_invitation_invitee_id_user")),
        sa.PrimaryKeyConstraint("token_hash", name=op.f("pk_invitation")),
    )
    op.create_index(op.f("ix_invitation_invitee_id"), "invitation", ["invitee_id"], unique=False)


def downgrade() -> None:
    """ Drop invitation table """
    op.drop_index(op.f("ix_invitation_invitee_id"), table_name="invitation")
    op.drop_table("invitation")

"""create_user

Revision ID: 0001
Revises:
Create Date: 2023-09-27 20:40:37.639208

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """ Create user table """
    op.create_table(
        'user',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False),
        sa.Column('master_pwd_hash', sa.String(), nullable=False),
        sa.Column('master_pwd_hint', sa.String(), nullable=True),
        sa.Column('last_pwd_change', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_email_change', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
        sa.UniqueConstraint('email', name=op.f('uq_user_email')),
    )
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)


def downgrade() -> None:
    """ Drop user table """
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_table('user')

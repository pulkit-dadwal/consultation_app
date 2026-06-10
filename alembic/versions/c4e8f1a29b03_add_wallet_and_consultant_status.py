"""Add wallet table and consultant status column

Revision ID: c4e8f1a29b03
Revises: a9c28ace1781
Create Date: 2026-06-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4e8f1a29b03'
down_revision: Union[str, Sequence[str], None] = 'a9c28ace1781'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

consultant_status = sa.Enum('online', 'offline', name='consultant_status')


def upgrade() -> None:
    """Upgrade schema."""
    consultant_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'wallets',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('balance', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    op.add_column(
        'consultants',
        sa.Column('status', consultant_status, nullable=False, server_default='online')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('consultants', 'status')
    op.drop_table('wallets')
    consultant_status.drop(op.get_bind(), checkfirst=True)

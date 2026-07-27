"""Add telegram fields and credits

Revision ID: 52a12c8a2b5e
Revises: 
Create Date: 2026-07-28 03:09:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '52a12c8a2b5e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to users table
    op.add_column('users', sa.Column('telegram_id', sa.BigInteger(), nullable=True))
    op.add_column('users', sa.Column('credits', sa.Integer(), nullable=False, server_default='3'))
    
    # Make email nullable
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True)
               
    # Make password nullable
    op.alter_column('users', 'hashed_password',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # Add index for telegram_id
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.alter_column('users', 'hashed_password',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('users', 'credits')
    op.drop_column('users', 'telegram_id')

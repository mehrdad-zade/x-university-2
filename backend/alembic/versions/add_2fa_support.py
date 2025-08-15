"""Add 2FA and email verification fields

Revision ID: add_2fa_support
Revises: add_user_security_fields
Create Date: 2025-08-15 02:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_2fa_support'
down_revision: Union[str, None] = 'add_user_security_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 2FA fields to users table
    op.add_column('users', sa.Column('totp_secret', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('backup_codes_generated_at', sa.DateTime(timezone=True), nullable=True))
    
    # Create user_recovery_codes table for 2FA backup codes
    op.create_table(
        'user_recovery_codes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('code_hash', sa.String(255), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_user_recovery_codes_user_id', 'user_recovery_codes', ['user_id'])
    op.create_index('ix_user_recovery_codes_code_hash', 'user_recovery_codes', ['code_hash'])


def downgrade() -> None:
    # Remove indexes
    op.drop_index('ix_user_recovery_codes_code_hash', 'user_recovery_codes')
    op.drop_index('ix_user_recovery_codes_user_id', 'user_recovery_codes')
    
    # Drop table
    op.drop_table('user_recovery_codes')
    
    # Remove columns from users table
    op.drop_column('users', 'backup_codes_generated_at')
    op.drop_column('users', 'two_factor_enabled')
    op.drop_column('users', 'totp_secret')

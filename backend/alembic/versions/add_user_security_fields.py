"""Add security and profile fields to users table

Revision ID: add_user_security_fields
Revises: 1692902edebf
Create Date: 2025-08-14 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_user_security_fields'
down_revision: Union[str, None] = '1692902edebf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add security and profile enhancement fields to users table."""
    
    # Add email verification fields
    op.add_column('users', sa.Column('email_verification_token', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('email_verification_sent_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_users_email_verification_token', 'users', ['email_verification_token'])
    
    # Add security fields
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('password_reset_token', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('password_reset_sent_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_users_password_reset_token', 'users', ['password_reset_token'])
    
    # Add profile and preferences fields
    op.add_column('users', sa.Column('profile_completed', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('terms_accepted', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('terms_accepted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('privacy_policy_accepted', sa.Boolean(), nullable=False, server_default='true'))
    
    # Add activity tracking fields
    op.add_column('users', sa.Column('last_password_change', sa.DateTime(timezone=True), nullable=True))
    
    # Update existing users to have terms accepted at creation time
    op.execute("""
        UPDATE users 
        SET terms_accepted_at = created_at 
        WHERE terms_accepted = true AND terms_accepted_at IS NULL
    """)


def downgrade() -> None:
    """Remove security and profile enhancement fields from users table."""
    
    # Remove indexes first
    op.drop_index('ix_users_password_reset_token', 'users')
    op.drop_index('ix_users_email_verification_token', 'users')
    
    # Remove columns
    op.drop_column('users', 'last_password_change')
    op.drop_column('users', 'privacy_policy_accepted')
    op.drop_column('users', 'terms_accepted_at')
    op.drop_column('users', 'terms_accepted')
    op.drop_column('users', 'profile_completed')
    op.drop_column('users', 'password_changed_at')
    op.drop_column('users', 'password_reset_sent_at')
    op.drop_column('users', 'password_reset_token')
    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'failed_login_attempts')
    op.drop_column('users', 'email_verification_sent_at')
    op.drop_column('users', 'email_verification_token')

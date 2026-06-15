"""seed test users and account

Revision ID: 269fbcc0487b
Revises: 86ed689e0bb7
Create Date: 2026-06-04 13:36:58.265465

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.services.security import hash_password


# revision identifiers, used by Alembic.
revision: str = '269fbcc0487b'
down_revision: Union[str, Sequence[str], None] = '86ed689e0bb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_hash = hash_password("user123")
    admin_hash = hash_password("admin123")

    op.execute(f"""
        INSERT INTO users (email, hashed_password, full_name, is_admin) VALUES
        ('user@test.com', '{user_hash}', 'Test User', false),
        ('admin@test.com', '{admin_hash}', 'Test Admin', true);
    """)

    op.execute(f"""
        INSERT INTO accounts (user_id, balance)
        SELECT id, 0.00 FROM users WHERE email = 'user@test.com';
    """)

def downgrade() -> None:
    op.execute("DELETE FROM accounts WHERE user_id IN (SELECT id FROM users WHERE email IN ('user@test.com', 'admin@test.com'));")
    op.execute("DELETE FROM users WHERE email IN ('user@test.com', 'admin@test.com');")

"""add expiring public share links

Revision ID: 605aec881c94
Revises: 07774c1c45b6
Create Date: 2026-10-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "605aec881c94"
down_revision: Union[str, Sequence[str], None] = "07774c1c45b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sharelink",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("file_id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("download_count", sa.Integer(), nullable=False),
        sa.Column("max_downloads", sa.Integer(), nullable=True),
        sa.Column("revoked", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["file.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sharelink_token_hash", "sharelink", ["token_hash"], unique=True)
    op.create_index("ix_sharelink_file_id", "sharelink", ["file_id"], unique=False)
    op.create_index("ix_sharelink_owner_id", "sharelink", ["owner_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sharelink_owner_id", table_name="sharelink")
    op.drop_index("ix_sharelink_file_id", table_name="sharelink")
    op.drop_index("ix_sharelink_token_hash", table_name="sharelink")
    op.drop_table("sharelink")

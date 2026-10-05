"""add general guest feedback submissions

Revision ID: 0005_general_feedback
Revises: 0004_guest_services
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_general_feedback"
down_revision = "0004_guest_services"
branch_labels = None
depends_on = None


def upgrade():
    if "guest_feedback" not in sa.inspect(op.get_bind()).get_table_names():
        op.create_table(
            "guest_feedback",
            sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("name", sa.String(150), nullable=False),
            sa.Column("email", sa.String(320), nullable=False),
            sa.Column("category", sa.String(40), nullable=False),
            sa.Column("rating", sa.Integer(), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("suggestions", sa.Text(), nullable=False, server_default=""),
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )


def downgrade():
    if "guest_feedback" in sa.inspect(op.get_bind()).get_table_names():
        op.drop_table("guest_feedback")

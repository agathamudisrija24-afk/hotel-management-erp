"""account and booking details

Revision ID: 0003_account_booking
Revises: 0002_hotel_experience
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_account_booking"
down_revision = "0002_hotel_experience"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    booking_columns = {column["name"] for column in inspector.get_columns("bookings")}
    if "phone" not in user_columns:
        op.add_column("users", sa.Column("phone", sa.String(30), nullable=False, server_default=""))
    if "guests" not in booking_columns:
        op.add_column("bookings", sa.Column("guests", sa.Integer(), nullable=False, server_default="1"))


def downgrade():
    op.drop_column("bookings", "guests")
    op.drop_column("users", "phone")

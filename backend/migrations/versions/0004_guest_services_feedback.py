"""extend guest service requests and reviews

Revision ID: 0004_guest_services
Revises: 0003_account_booking
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_guest_services"
down_revision = "0003_account_booking"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    service_columns = {column["name"] for column in inspector.get_columns("service_requests")}
    review_columns = {column["name"] for column in inspector.get_columns("reviews")}
    for name, column in (
        ("room_number", sa.Column("room_number", sa.String(30), nullable=False, server_default="")),
        ("preferred_time", sa.Column("preferred_time", sa.String(80), nullable=False, server_default="")),
        ("category", sa.Column("category", sa.String(100), nullable=False, server_default="")),
    ):
        if name not in service_columns:
            op.add_column("service_requests", column)
    for name, column in (
        ("cleanliness_rating", sa.Column("cleanliness_rating", sa.Integer(), nullable=False, server_default="5")),
        ("staff_rating", sa.Column("staff_rating", sa.Integer(), nullable=False, server_default="5")),
        ("comfort_rating", sa.Column("comfort_rating", sa.Integer(), nullable=False, server_default="5")),
        ("dining_rating", sa.Column("dining_rating", sa.Integer(), nullable=True)),
    ):
        if name not in review_columns:
            op.add_column("reviews", column)


def downgrade():
    op.drop_column("reviews", "dining_rating")
    op.drop_column("reviews", "comfort_rating")
    op.drop_column("reviews", "staff_rating")
    op.drop_column("reviews", "cleanliness_rating")
    op.drop_column("service_requests", "category")
    op.drop_column("service_requests", "preferred_time")
    op.drop_column("service_requests", "room_number")

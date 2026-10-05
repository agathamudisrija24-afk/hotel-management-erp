"""hotel experience metadata

Revision ID: 0002_hotel_experience
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_hotel_experience"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    def add_if_missing(table, column):
        if column.name not in {item["name"] for item in inspector.get_columns(table)}:
            op.add_column(table, column)
    # 0001 creates metadata dynamically in this project. These guards also make
    # the revision correct for a new database and an existing 0001 database.
    add_if_missing("hotels", sa.Column("rating", sa.Numeric(2, 1), nullable=False, server_default="4.5"))
    add_if_missing("hotels", sa.Column("hotel_type", sa.String(60), nullable=False, server_default="Hotel"))
    add_if_missing("hotel_amenities", sa.Column("description", sa.String(240), nullable=False, server_default=""))
    add_if_missing("food_items", sa.Column("description", sa.Text(), nullable=False, server_default=""))
    add_if_missing("food_items", sa.Column("vegetarian", sa.Boolean(), nullable=False, server_default=sa.true()))
    add_if_missing("food_items", sa.Column("image_url", sa.Text(), nullable=False, server_default=""))


def downgrade():
    op.drop_column("food_items", "image_url")
    op.drop_column("food_items", "vegetarian")
    op.drop_column("food_items", "description")
    op.drop_column("hotel_amenities", "description")
    op.drop_column("hotels", "hotel_type")
    op.drop_column("hotels", "rating")

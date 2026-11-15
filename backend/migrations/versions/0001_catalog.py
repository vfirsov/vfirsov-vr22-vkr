"""Create categories and products for the storefront."""

from alembic import op
import sqlalchemy as sa

revision = "0001_catalog"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False, unique=True),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="RESTRICT")),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("slug", sa.String(160), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("origin_country", sa.String(120), nullable=False),
        sa.Column("origin_region", sa.String(160), nullable=False),
        sa.Column("packaging_weight", sa.Integer(), nullable=False),
        sa.Column("brewing_recommendation", sa.Text()),
        sa.Column("image_url", sa.Text()),
        sa.Column("in_stock", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.CheckConstraint("price >= 0", name="ck_products_price"),
        sa.CheckConstraint("packaging_weight > 0", name="ck_products_weight"),
    )
    op.create_index("ix_products_category_active", "products", ["category_id", "is_active"])


def downgrade():
    op.drop_table("products")
    op.drop_table("categories")

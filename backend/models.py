"""The two catalogue tables used by the read-only storefront."""

from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"))


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_products_price"),
        CheckConstraint("packaging_weight > 0", name="ck_products_weight"),
        Index("ix_products_category_active", "category_id", "is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"))
    slug: Mapped[str] = mapped_column(String(160), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    origin_country: Mapped[str] = mapped_column(String(120))
    origin_region: Mapped[str] = mapped_column(String(160), default="")
    packaging_weight: Mapped[int] = mapped_column(Integer)
    brewing_recommendation: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    category: Mapped[Category] = relationship(lazy="joined")

    def as_catalog_item(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "category": self.category.name,
            "origin": ", ".join(part for part in (self.origin_country, self.origin_region) if part),
            "description": self.description,
            "price": int(self.price) if self.price == self.price.to_integral_value() else float(self.price),
            "weightGrams": self.packaging_weight,
            "inStock": self.in_stock,
        }

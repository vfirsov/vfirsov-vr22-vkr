"""Apply catalogue migrations and import demo data without overwriting edits."""

import argparse
import json
import os
from decimal import Decimal
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import catalog_engine
from models import Category, Product


ROOT = Path(__file__).resolve().parent
CATEGORY_SLUGS = {
    "Зелёный чай": "green-tea",
    "Улун": "oolong",
    "Красный чай": "red-tea",
    "Чёрный чай": "black-tea",
    "Белый чай": "white-tea",
    "Пуэр": "puer",
    "Травяной напиток": "herbal-tea",
}


def upgrade_catalog(engine):
    config = Config()
    config.set_main_option("script_location", str(ROOT / "migrations"))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")


def seed_catalog(engine, source=ROOT / "catalog.json"):
    with Session(engine) as session, session.begin():
        # Do not overwrite an existing catalogue on repeated deploys.
        if session.scalar(select(func.count()).select_from(Product)):
            return 0
        items = json.loads(Path(source).read_text(encoding="utf-8"))
        categories = {category.slug: category for category in session.scalars(select(Category))}
        for item in items:
            name = item["category"]
            slug = CATEGORY_SLUGS[name]
            if slug not in categories:
                categories[slug] = Category(name=name, slug=slug)
                session.add(categories[slug])
            country, _, region = item["origin"].partition(", ")
            session.add(Product(
                category=categories[slug], slug=item["slug"], name=item["name"],
                description=item["description"], price=Decimal(str(item["price"])),
                origin_country=country, origin_region=region,
                packaging_weight=item["weightGrams"], in_stock=item["inStock"], is_active=True,
            ))
        return len(items)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("upgrade", "seed", "prepare", "check"))
    args = parser.parse_args()
    url = os.environ.get("DATABASE_URL")
    if not url:
        parser.error("Set DATABASE_URL before running this command")
    engine = catalog_engine(url)
    try:
        if args.operation in {"upgrade", "prepare"}:
            upgrade_catalog(engine)
            print("Catalogue schema is up to date", flush=True)
        if args.operation in {"seed", "prepare"}:
            print(f"Imported demo products: {seed_catalog(engine)}", flush=True)
        if args.operation == "check":
            with Session(engine) as session:
                counts = {model.__tablename__: session.scalar(select(func.count()).select_from(model))
                          for model in (Category, Product)}
                print(json.dumps(counts))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()

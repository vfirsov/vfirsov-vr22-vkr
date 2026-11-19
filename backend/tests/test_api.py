import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import FRONTEND_ORIGINS, create_app
from manage_catalog import seed_catalog, upgrade_catalog
from models import Base, Product


class CatalogApiTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.database_url = f"sqlite:///{Path(self.directory.name) / 'catalog.db'}"
        self.app = create_app({"TESTING": True, "DATABASE_URL": self.database_url})
        self.engine = self.app.extensions["catalog_engine"]
        self.addCleanup(self.engine.dispose)
        upgrade_catalog(self.engine)
        seed_catalog(self.engine)
        self.client = self.app.test_client()

    def test_catalog_contract(self):
        response = self.client.get("/api/catalog")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        data = response.get_json()
        self.assertEqual(data["currency"], "RUB")
        self.assertEqual(data["total"], 12)
        self.assertEqual(data["total"], len(data["items"]))
        self.assertEqual(len({item["id"] for item in data["items"]}), 12)
        self.assertEqual(len({item["slug"] for item in data["items"]}), 12)
        for item in data["items"]:
            self.assertEqual(set(item), {"id", "slug", "name", "category", "origin", "description", "price", "weightGrams", "inStock"})
            self.assertGreater(item["price"], 0)
            self.assertGreater(item["weightGrams"], 0)
            self.assertIsInstance(item["inStock"], bool)
            for key in ("name", "category", "origin", "description"):
                self.assertTrue(item[key])
        self.assertIn("Лун Цзин", response.get_data(as_text=True))
        source = json.loads((Path(__file__).resolve().parents[1] / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(data["items"], source)

    def test_catalog_reads_data_on_each_request(self):
        self.client.get("/api/catalog")
        with Session(self.engine) as session, session.begin():
            product = session.scalar(select(Product).where(Product.slug == "longjing"))
            product.name = "Изменённый чай"
            product.price = Decimal("699.50")
            product.in_stock = False
            session.scalar(select(Product).where(Product.slug == "sencha")).is_active = False
        data = self.client.get("/api/catalog").get_json()
        self.assertEqual(data["total"], 11)
        self.assertEqual(data["items"][0]["name"], "Изменённый чай")
        self.assertEqual(data["items"][0]["price"], 699.5)
        self.assertFalse(data["items"][0]["inStock"])
        self.assertNotIn("sencha", {item["slug"] for item in data["items"]})

    def test_database_failure_returns_service_unavailable(self):
        with self.engine.begin() as connection:
            connection.execute(text("DROP TABLE products"))
        with self.assertLogs(self.app.logger, level="ERROR"):
            response = self.client.get("/api/catalog")
        self.assertEqual(response.status_code, 503)
        self.assertIn("error", response.get_json())

    def test_repeated_prepare_preserves_changes_and_data_survives_new_app(self):
        with Session(self.engine) as session, session.begin():
            session.scalar(select(Product).where(Product.slug == "longjing")).price = Decimal("1234")
        upgrade_catalog(self.engine)
        self.assertEqual(seed_catalog(self.engine), 0)
        other_app = create_app({"TESTING": True, "DATABASE_URL": self.database_url})
        self.addCleanup(other_app.extensions["catalog_engine"].dispose)
        data = other_app.test_client().get("/api/catalog").get_json()
        self.assertEqual(data["total"], 12)
        self.assertEqual(data["items"][0]["price"], 1234)

    def test_migration_matches_models(self):
        with self.engine.connect() as connection:
            self.assertEqual(compare_metadata(MigrationContext.configure(connection), Base.metadata), [])

    def test_database_enforces_price_weight_and_category(self):
        for statement in (
            "UPDATE products SET price = -1 WHERE id = 1",
            "UPDATE products SET packaging_weight = 0 WHERE id = 1",
            "UPDATE products SET category_id = 999999 WHERE id = 1",
            "UPDATE products SET slug = 'longjing' WHERE id = 2",
        ):
            with self.subTest(statement=statement), self.assertRaises(IntegrityError):
                with self.engine.begin() as connection:
                    connection.execute(text(statement))

    def test_missing_database_url_returns_service_unavailable(self):
        app = create_app({"TESTING": True, "DATABASE_URL": None})
        with self.assertLogs(app.logger, level="ERROR"):
            self.assertEqual(app.test_client().get("/api/catalog").status_code, 503)

    def test_catalog_cors_allows_frontend_origin_only(self):
        origin = next(iter(FRONTEND_ORIGINS))
        response = self.client.get("/api/catalog", headers={"Origin": origin})
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), origin)
        self.assertEqual(response.headers.get("Vary"), "Origin")
        preflight = self.client.options("/api/catalog", headers={"Origin": origin})
        self.assertEqual(preflight.status_code, 200)
        self.assertEqual(preflight.headers.get("Access-Control-Allow-Origin"), origin)
        self.assertEqual(preflight.headers.get("Access-Control-Allow-Methods"), "GET, OPTIONS")
        foreign = self.client.get("/api/catalog", headers={"Origin": "https://example.com"})
        self.assertNotIn("Access-Control-Allow-Origin", foreign.headers)

    def test_health_and_unknown_route(self):
        self.assertEqual(self.client.get("/healthz").get_json(), {"status": "ok"})
        response = self.client.get("/missing")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "application/json")


if __name__ == "__main__":
    unittest.main()

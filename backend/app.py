"""Read-only demo tea catalogue consumed by the Nuxt server and the browser."""

import os

from flask import Flask, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import catalog_engine
from models import Product

# Origins allowed to read the catalogue from the browser (client-side navigation).
FRONTEND_ORIGINS = frozenset({
    "https://tea-shop-frontend-demo-vfirsov.msk1.amvera.tech",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
})


def create_app(test_config=None):
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.config.from_mapping(DATABASE_URL=os.environ.get("DATABASE_URL"))
    if test_config:
        app.config.update(test_config)
    engine = catalog_engine(app.config["DATABASE_URL"]) if app.config["DATABASE_URL"] else None
    app.extensions["catalog_engine"] = engine

    @app.get("/healthz")
    def health():
        return jsonify(status="ok")

    @app.get("/api/catalog")
    def catalog():
        if engine is None:
            app.logger.error("DATABASE_URL is not configured")
            return jsonify(error="Каталог временно недоступен"), 503
        try:
            with Session(engine) as session:
                products = session.scalars(select(Product).where(Product.is_active.is_(True)).order_by(Product.id))
                items = [product.as_catalog_item() for product in products]
        except SQLAlchemyError:
            app.logger.exception("Unable to query catalogue database")
            return jsonify(error="Каталог временно недоступен"), 503
        return jsonify(items=items, total=len(items), currency="RUB")

    @app.after_request
    def no_cache(response):
        response.headers["Cache-Control"] = "no-store"
        origin = request.headers.get("Origin")
        if origin in FRONTEND_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
            if request.method == "OPTIONS":
                response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        return response

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify(error="Маршрут не найден"), 404

    return app


app = create_app()

"""MediAssist -- Medical Symptom Checker & Knowledge Base.

Flask entry point. Run with: python app.py
"""

import os
import sys

from flask import Flask

import config
from models.database import db, init_db
from routes.api import api_bp
from routes.views import views_bp


def create_app(testing: bool = False) -> Flask:
    """Application factory for MediAssist."""
    app = Flask(__name__)

    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = testing

    if testing:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    os.makedirs(os.path.join(config.BASE_DIR, "instance"), exist_ok=True)

    db.init_app(app)
    init_db(app)

    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)

    @app.context_processor
    def inject_globals():
        return {
            "app_name": "MediAssist",
            "app_version": "1.0.0",
        }

    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def server_error(e):
        return {"error": "Internal server error"}, 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8011, debug=config.DEBUG)

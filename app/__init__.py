from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from .authentication.urls import register_auth_blueprint
from .authentication.views import *  # pyright: ignore
from .config import dev_config
from .extensions import api, db


def create_app(config=None):
    """Application factory function."""
    app = Flask(__name__)
    config = config or dev_config
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    api.init_app(app)
    Migrate(app, db)
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .authentication.models import User

        return db.session.get(User, int(user_id))

    with app.app_context():
        if config:
            db.create_all()
        from .extensions import create_admin

        create_admin()

    # Register blueprints (authentication routes, etc.)
    register_auth_blueprint(app, api)

    # A simple home route
    @app.route("/hello")
    def hello():
        return "<h1>Hello Flask</h1>"

    return app

import pytest

from app import create_app
from app.config import AppConfig
from app.extensions import db

# Create a configuration for testing
test_config = AppConfig(
    SECRET_KEY="this-is-secret",
    SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    TESTING=True,
)


@pytest.fixture
def app():
    app = create_app(test_config)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()

import pytest

from app import AppSetup
from .config import test_config


@pytest.fixture
def app():
    app = AppSetup.app
    app.config.from_object(test_config)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello" in response.data

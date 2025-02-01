import pytest

from app import AppSetup


@pytest.fixture
def app():
    app = AppSetup.app
    app.config["TESTING"] = True
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello" in response.data

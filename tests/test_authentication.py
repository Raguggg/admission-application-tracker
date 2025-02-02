from flask.testing import FlaskClient
from werkzeug.wrappers.response import Response


def test_register(client: FlaskClient):
    """
    Test that a new user (non-admin) can be registered.
    """
    response: Response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "password123",
            "role": "user",
        },
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data.get("message") == "User created successfully"


def test_login(client: FlaskClient):
    """
    Test that a registered user can log in.
    """
    register_response: Response = client.post(
        "/auth/register",
        json={
            "name": "Login User",
            "email": "loginuser@example.com",
            "password": "password123",
            "role": "user",
        },
        headers={"Content-Type": "application/json"},
    )
    assert register_response.status_code == 201

    login_response: Response = client.post(
        "/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "password123",
        },
        headers={"Content-Type": "application/json"},
    )
    assert login_response.status_code == 200
    data = login_response.get_json()
    assert "Logged in successfully." in data.get("message")
    assert data.get("name") == "Login User"
    assert data.get("is_admin") is False


def test_logout(client: FlaskClient):
    """
    Test that a logged-in user can log out.
    """
    register_response: Response = client.post(
        "/auth/register",
        json={
            "name": "Logout User",
            "email": "logoutuser@example.com",
            "password": "password123",
            "role": "user",
        },
        headers={"Content-Type": "application/json"},
    )
    assert register_response.status_code == 201

    login_response: Response = client.post(
        "/auth/login",
        json={
            "email": "logoutuser@example.com",
            "password": "password123",
        },
        headers={"Content-Type": "application/json"},
    )
    assert login_response.status_code == 200

    logout_response: Response = client.post("/auth/logout")
    assert logout_response.status_code == 200
    data = logout_response.get_json()
    assert data.get("message") == "Logged out successfully."


def test_login_admin(client: FlaskClient):
    """
    Test that a admin user can log in.
    """

    login_response: Response = client.post(
        "/auth/login",
        json={
            "email": "admin@gmail.com",
            "password": "admin",
        },
        headers={"Content-Type": "application/json"},
    )
    assert login_response.status_code == 200
    data = login_response.get_json()
    assert "Logged in successfully." in data.get("message")
    assert data.get("name") == "admin"
    assert data.get("is_admin") is True

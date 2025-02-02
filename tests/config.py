from app.config import AppConfig

test_config = AppConfig(
    SECRET_KEY="this-is-secret",
    SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    TESTING=True,
)

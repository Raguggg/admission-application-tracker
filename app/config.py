from dataclasses import dataclass


@dataclass
class AppConfig:
    SECRET_KEY: str
    SQLALCHEMY_DATABASE_URI: str
    DEBUG: bool = False
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    TESTING: bool = False


dev_config = AppConfig(
    SECRET_KEY="this-is-secret",
    SQLALCHEMY_DATABASE_URI="sqlite:///app.db",
    DEBUG=True,
)

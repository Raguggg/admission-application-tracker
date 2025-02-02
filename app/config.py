from dataclasses import dataclass
from pathlib import Path


class FileConfig:
    BASE_DIR = Path(__file__).parent.parent
    UPLOAD_FILE = BASE_DIR / "UPLOADS"
    ADMISSION_LETTER = BASE_DIR / "ADMISSION_LETTER"
    UPLOAD_FILE.mkdir(parents=True, exist_ok=True)
    ADMISSION_LETTER.mkdir(parents=True, exist_ok=True)


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

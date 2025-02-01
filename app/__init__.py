from flask import Flask

from app.config import dev_config


class AppSetup:
    app = Flask(__name__)


def create_app():
    AppSetup.app.config.from_object(dev_config)

    return AppSetup.app


@AppSetup.app.route("/")
def home():
    return "<h1>Hello Flask</h1>"

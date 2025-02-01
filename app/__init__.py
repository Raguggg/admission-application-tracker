from flask import Flask


class AppSetup:
    app = Flask(__name__)


@AppSetup.app.route("/")
def home():
    return "<h1>Hello Flask</h1>"

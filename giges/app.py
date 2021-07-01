import connexion
from connexion.apps.flask_app import FlaskApp
from connexion.resolver import RestyResolver
from flask import Flask


class App(FlaskApp):
    def create_app(self) -> Flask:
        app = Flask(__name__)
        return app


def create_connexion_app() -> connexion.App:
    connexion_app = App(__package__, specification_dir="schemas/")

    connexion_app.add_api(
        "api.yml",
        validate_responses=True,
        strict_validation=True,
        resolver=RestyResolver("giges.handlers"),
    )

    return connexion_app


def create_flask_app() -> Flask:
    return create_connexion_app().app

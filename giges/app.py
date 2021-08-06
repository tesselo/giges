import os
from typing import Any, Optional

import connexion
from connexion.apps.flask_app import FlaskApp
from connexion.resolver import RestyResolver
from flask import Flask

SETTINGS_VARIABLE_NAME = "GIGES_SETTINGS"


class App(FlaskApp):
    def create_app(self) -> Flask:
        app = Flask(__name__)
        return app


def create_connexion_app(
    settings_object: Optional[Any] = None, **kwargs: int
) -> connexion.App:
    if settings_object is None:
        settings_object = os.getenv(SETTINGS_VARIABLE_NAME)
        if settings_object is None:
            raise RuntimeError(
                f"The environment variable {SETTINGS_VARIABLE_NAME} "
                f"is not set and as such configuration "
                f"could not be loaded. "
                f"Set this variable and make it point to a configuration file"
            )

    connexion_app = App(__package__, specification_dir="schemas/")
    flask_app = connexion_app.app
    flask_app.config.from_object(settings_object)
    flask_app.config.update(**kwargs)

    connexion_app.add_api(
        "api.yml",
        validate_responses=True,
        strict_validation=True,
        resolver=RestyResolver("giges.handlers"),
    )

    return connexion_app


def create_flask_app() -> Flask:
    return create_connexion_app().app

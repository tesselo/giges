import logging
import os
import sys
from typing import Any, Optional

import connexion
import structlog
from connexion.apps.flask_app import FlaskApp
from connexion.resolver import RestyResolver
from flask import Flask
from flask_migrate import Migrate

SETTINGS_VARIABLE_NAME = "GIGES_SETTINGS"


class App(FlaskApp):
    def create_app(self) -> Flask:
        app = Flask(__name__)
        return app


def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s", stream=sys.stdout, level=logging.INFO
    )


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

    from .db import db

    db.init_app(flask_app)
    db.app = flask_app

    Migrate(flask_app, db)

    configure_logging()

    return connexion_app


def create_flask_app() -> Flask:
    return create_connexion_app().app

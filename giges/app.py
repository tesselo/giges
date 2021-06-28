import connexion
from connexion_compose import compile_schema
from connexion.apps.flask_app import FlaskApp
from connexion.resolver import RestyResolver
from flask import Flask

class App(FlaskApp):
    def create_app(self):
        app = Flask(__name__)
        return app

def create_connexion_app():
    connexion_app = App(__package__)
    flask_app = connexion_app.app
    
    connexion_app.add_api(
            compile_schema('giges/schemas'),
            validate_responses=True,
            strict_validation=True,
            resolver=RestyResolver("giges.handlers")
    )

    return connexion_app



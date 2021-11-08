from flask import current_app

from giges.app import create_flask_app

app = current_app or create_flask_app()

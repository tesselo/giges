import pytest

from giges.app import create_connexion_app


@pytest.fixture(scope="session")
def connexion_app(root_dir):
    return create_connexion_app()


@pytest.fixture(scope="session")
def app(connexion_app):
    app = connexion_app.app

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client

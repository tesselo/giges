import flask_migrate
import pytest
from pytest_factoryboy import register
from sqlalchemy import inspect

from giges.app import create_connexion_app
from giges.db import db
from .factories import EventFactory, ProjectFactory, WebhookFactory

for factory in (EventFactory, ProjectFactory, WebhookFactory):
    register(factory)


@pytest.fixture(scope="session")
def connexion_app():
    return create_connexion_app()


@pytest.fixture(scope="session")
def app(connexion_app):
    app = connexion_app.app

    with app.app_context():
        yield app


@pytest.fixture
def cli_runner(app):
    yield app.test_cli_runner()


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="session")
def _db(app):
    assert inspect(db.engine).get_table_names() in (
        [],
        ["alembic_version"],
    ), "test database not empty, cautionary stopping this"

    flask_migrate.upgrade()

    yield db

    db.session.rollback()  # required if some test fails

    flask_migrate.downgrade(revision="base")
    db.metadata.drop_all(db.engine)
    db.engine.execute("DROP TABLE IF EXISTS alembic_version")


@pytest.fixture(autouse=True)
def transactional_db(_db):
    yield _db.session
    _db.session.rollback()
    for table in reversed(_db.metadata.sorted_tables):
        _db.session.execute(table.delete())
    _db.session.commit()


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "decode_compressed_response": True,
        "filter_headers": ["authorization"],
    }

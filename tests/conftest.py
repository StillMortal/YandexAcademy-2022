import pytest

from api.app import app, db


@pytest.fixture(scope="session")
def flask_app():
    app.testing = True

    return app.test_client()


@pytest.fixture(scope="function")
def empty_db():
    db.drop_all()
    db.create_all()

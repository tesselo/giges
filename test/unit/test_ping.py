from giges.handlers import health


def test_ping():
    response, status = health.ping()
    assert response["pong"]
    assert status == 200

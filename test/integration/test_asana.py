from giges.models.asana import Event, Webhook


def test_asana_projects_handshake(client, transactional_db):
    secret = "wow_such_very_secret"
    webhook = Webhook(path="/asana/projects")
    transactional_db.add(webhook)
    transactional_db.commit()

    response = client.post(
        "/asana/projects",
        headers={"X-Hook-Secret": secret},
        json={},
    )
    assert response.status_code == 204
    assert response.headers["X-Hook-Secret"] == secret
    assert webhook.secret == secret


def test_asana_projects_handshake_no_webhook(client):
    response = client.post(
        "/asana/projects",
        headers={"X-Hook-Secret": "whatever"},
        json={},
    )
    assert response.status_code == 404


def test_asana_projects_handshake_hack_attempt(client, transactional_db):
    secret = "wow_such_very_secret"
    webhook = Webhook(path="/asana/projects", secret=secret)
    transactional_db.add(webhook)
    transactional_db.commit()

    response = client.post(
        "/asana/projects",
        headers={"X-Hook-Secret": "evil hacker"},
        json={},
    )
    assert response.status_code == 400
    assert webhook.secret == secret


def test_asana_project_event_no_secret(client, transactional_db):
    webhook = Webhook(path="/asana/projects")
    transactional_db.add(webhook)
    transactional_db.commit()

    response = client.post(
        "/asana/projects",
        headers={"X-Hook-Signature": "wow_such_very_secret_signature"},
        json={"events": [{"glitch": "in matrix"}]},
    )
    assert response.status_code == 500
    assert Event.query.count() == 0


def test_asana_project_event_bad_signature(client, transactional_db):
    webhook = Webhook(path="/asana/projects", secret="pork_fillet")
    transactional_db.add(webhook)
    transactional_db.commit()

    response = client.post(
        "/asana/projects",
        headers={
            "X-Hook-Signature": "I am a bad cracker wanting to crack the pipe"
        },
        json={"events": [{"glitch": "in matrix"}]},
    )
    assert response.status_code == 400
    assert Event.query.count() == 0


def test_asana_project_event_ok(client, transactional_db):
    signature = (
        "56302af223b5cfad770ff07469189e5a2ac961bf77ac6fcf000ae75c619af3d7"
    )
    assert Event.query.count() == 0
    webhook = Webhook(path="/asana/projects", secret="pork_fillet")
    transactional_db.add(webhook)
    transactional_db.commit()

    response = client.post(
        "/asana/projects",
        headers={"X-Hook-Signature": signature},
        json={"events": [{"glitch": "in matrix"}]},
    )
    assert response.status_code == 204
    assert Event.query.count() == 1


def test_asana_project_event_no_events(client):
    response = client.post(
        "/asana/projects",
        headers={"X-Hook-Signature": "wow_such_very_secret_signature"},
    )
    assert response.status_code == 400


def test_asana_project_event_no_signature(client):
    response = client.post("/asana/projects", json={"events": []})
    assert response.status_code == 400

import pytest

from giges.models.asana import Event, Task


def test_asana_tasks_handshake(client, webhook):
    secret = "wow_such_very_secret"
    webhook.secret = None

    response = client.post(
        webhook.path,
        headers={"X-Hook-Secret": secret},
        json={},
    )
    assert response.status_code == 204
    assert response.headers["X-Hook-Secret"] == secret
    assert webhook.secret == secret


def test_asana_task_handshake_no_webhook(client):
    response = client.post(
        "/asana/projects/666",
        headers={"X-Hook-Secret": "whatever"},
        json={},
    )
    assert response.status_code == 404


def test_asana_task_handshake_hack_attempt(client, webhook):
    secret = webhook.secret

    response = client.post(
        webhook.path,
        headers={"X-Hook-Secret": "evil hacker"},
        json={},
    )
    assert response.status_code == 400
    assert webhook.secret == secret


def test_asana_task_event_no_secret(client, webhook):
    webhook.secret = None
    response = client.post(
        webhook.path,
        headers={"X-Hook-Signature": "wow_such_very_secret_signature"},
        json={"events": [{"glitch": "in matrix"}]},
    )
    assert response.status_code == 500
    assert Event.query.count() == 0


def test_asana_task_event_bad_signature(client, webhook):
    response = client.post(
        webhook.path,
        headers={
            "X-Hook-Signature": "I am a bad cracker wanting to crack the pipe"
        },
        json={"events": [{"glitch": "in matrix"}]},
    )
    assert response.status_code == 400
    assert Event.query.count() == 0


def test_asana_task_event_bad_format(client, webhook):
    signature = (
        "56302af223b5cfad770ff07469189e5a2ac961bf77ac6fcf000ae75c619af3d7"
    )
    assert Event.query.count() == 0
    webhook.secret = "pork_fillet"

    response = client.post(
        webhook.path,
        headers={"X-Hook-Signature": signature},
        json={"events": [{"glitch": "in matrix"}]},
    )
    assert response.status_code == 400
    assert Event.query.count() == 0


@pytest.mark.vcr
def test_asana_task_event_ok(client, webhook):
    signature = (
        "e9f6f5a3b6900a7556d5d86774ba5b1a143a963763006523b630d82aed4e4809"
    )
    assert Task.query.count() == 0
    assert Event.query.count() == 0
    webhook.secret = "pork_fillet"

    response = client.post(
        webhook.path,
        headers={"X-Hook-Signature": signature},
        json={
            "events": [
                {
                    "user": {
                        "gid": "1200279241225750",
                        "resource_type": "user",
                    },
                    "created_at": "2021-09-28T18:39:13.594Z",
                    "action": "changed",
                    "parent": None,
                    "change": {"field": "completed_at", "action": "changed"},
                    "resource": {
                        "gid": "1201046407912294",
                        "resource_type": "task",
                        "resource_subtype": "default_task",
                    },
                }
            ]
        },
    )
    assert response.status_code == 204
    assert Event.query.count() == 1
    assert Task.query.count() == 1


def test_asana_task_event_no_events(client):
    response = client.post(
        "/asana/projects/666",
        headers={"X-Hook-Signature": "wow_such_very_secret_signature"},
    )
    assert response.status_code == 400


def test_asana_task_event_no_signature(client, webhook):
    response = client.post(webhook.path, json={"events": []})
    assert response.status_code == 400

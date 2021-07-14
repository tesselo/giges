def test_asana_projects_handshake(client):
    response = client.post(
        "/asana/projects",
        headers={"X-Hook-Secret": "wow_such_very_secret"},
        json={},
    )
    assert response.status_code == 204
    assert response.headers["X-Hook-Secret"] == "wow_such_very_secret"


def test_asana_project_event_ok(client):
    response = client.post(
        "/asana/projects",
        headers={"X-Hook-Signature": "wow_such_very_secret_signature"},
        json={"events": [{"glitch": "in matrix"}]},
    )
    assert response.status_code == 204


def test_asana_project_event_no_events(client):
    response = client.post(
        "/asana/projects",
        headers={"X-Hook-Signature": "wow_such_very_secret_signature"},
    )
    assert response.status_code == 400


def test_asana_project_event_no_signature(client):
    response = client.post("/asana/projects", json={"events": []})
    assert response.status_code == 400

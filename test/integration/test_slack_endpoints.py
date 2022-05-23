import pytest


@pytest.mark.parametrize(
    "logs_url,meeting_url,blocks",
    [
        ("https://example.com/logs", "https://example.com/meeting", 3),
        ("https://example.com/logs", None, 2),
        (None, "https://example.com/meeting", 2),
        (None, None, 1),
    ],
)
def test_slack_command_ritual(client, ritual, logs_url, meeting_url, blocks):

    ritual.logs_url = logs_url
    ritual.meeting_url = meeting_url
    response = client.post(
        "/slack/commands/ritual",
        data={
            "command": "/ritual",
            "text": ritual.name,
            "user_name": "Tesserito",
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 200
    assert response.json
    assert len(response.json["blocks"]) == blocks


def test_slack_command_wrong_ritual(client):

    response = client.post(
        "/slack/commands/ritual",
        data={
            "command": "/ritual",
            "text": "christmas",
            "user_name": "Tesserito",
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 404, response


def test_slack_command_ritual_bad_data(client, ritual):

    response = client.post(
        "/slack/commands/ritual",
        data={"command": "/ritual", "text": ritual.name, "deity": "Tesserito"},
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 400, response


def test_slack_command_random_selection(client):

    response = client.post(
        "/slack/commands/random_humans",
        data={"command": "/random_human", "text": "there was upon a time"},
    )

    assert response.status_code == 200
    assert response.json
    assert len(response.json["blocks"]) == 6


def test_slack_command_random_selection_no_humans(client):

    response = client.post(
        "/slack/commands/random_humans",
        data={"command": "/random_human", "text": ""},
    )

    assert response.status_code == 200
    assert response.json
    assert "YES, YES" in response.json["blocks"][-1]["text"]["text"]

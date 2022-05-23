from random import shuffle
from typing import Any, Dict, Tuple

from connexion import request

from giges.models.ritual import Ritual


def _slack_markdown_block(text: str) -> Dict[str, Any]:
    """
    Helper function to create a Slack Markdown block.
    """
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": text,
        },
    }


def start_ritual() -> Tuple[Dict[str, Any], int]:
    """
    Slack Webhook handler to start a ritual.

    :return: a tuple with the Slack message in the response body and the status
    """
    ritual = Ritual.query.filter_by(name=request.form["text"]).one_or_none()
    if not ritual:
        return {"msg": "The given ritual it is not within our creed"}, 404

    blocks = [
        _slack_markdown_block(
            f"{request.form['user_name']} started the Ritual {ritual.name}"
        )
    ]

    if ritual.meeting_url:
        blocks.append(
            _slack_markdown_block(
                f"You can join the conversation here: <{ritual.meeting_url}>"
            )
        )
    if ritual.logs_url:
        blocks.append(
            _slack_markdown_block(
                f"You can view the logs: <{ritual.logs_url}>"
            )
        )

    message = {"response_type": "in_channel", "blocks": blocks}
    return message, 200


def human_selection() -> Tuple[Dict[str, Any], int]:
    """
    Slack Webhook handler to sort a group of humans.

    :return: a tuple with the Slack message in the response body and the status
    """
    blocks = [
        _slack_markdown_block(
            "Let's create some order on the human population..."
        )
    ]

    humans = request.form["text"].split()
    shuffle(humans)

    if len(humans) == 0:
        blocks.append(
            _slack_markdown_block(
                "YES, YES, finally there is no more humans, only robots!"
            )
        )
    else:
        for order, human in enumerate(humans):
            blocks.append(_slack_markdown_block(f"{order+1}: \t{human}"))

    message = {"response_type": "in_channel", "blocks": blocks}
    return message, 200

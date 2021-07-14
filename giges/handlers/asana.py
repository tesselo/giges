import logging
from typing import Dict, Tuple, Union

from connexion import request


def projects() -> Union[Tuple[Dict, int], Tuple[Dict, int, Dict[str, str]]]:
    """
    Handle incoming webhooks from asana related to projects.

    When registering a webhook, asana will first send a request with a secret,
    X-Hook-Secret, that we can use later to verify the authenticity of the
    rest of the webhooks requests using X-Hook-Signature.

    But we are not doing such check for the first implementation.

    :return: - a tuple with an empty body and the status
             - a tuple with an empty body, the status and the handshake header
    """
    if not request.headers.get("X-Hook-Secret") and not request.headers.get(
        "X-Hook-Signature"
    ):
        return {}, 400
    if request.headers.get("X-Hook-Secret"):
        return {}, 204, {"X-Hook-Secret": request.headers["X-Hook-Secret"]}

    logging.info(request.json["events"])
    return {}, 204

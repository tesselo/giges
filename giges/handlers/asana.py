import hashlib
import hmac
from typing import Dict, Tuple, Union

import structlog
from connexion import request

from giges.db import db
from giges.models.asana import Event, Webhook

logger = structlog.get_logger(__name__)


def projects() -> Union[Tuple[Dict, int], Tuple[Dict, int, Dict[str, str]]]:
    """
    Handle incoming webhooks from asana related to projects.

    When registering a webhook, asana will first send a request with a secret,
    X-Hook-Secret, that we use to verify the authenticity of the rest of the
    webhooks requests using X-Hook-Signature.

    :return: - a tuple with an empty body and the status
             - a tuple with an empty body, the status and the handshake header
    """
    secret = request.headers.get("X-Hook-Secret")
    signature = request.headers.get("X-Hook-Signature")

    if not secret and not signature:
        return {"msg": "Invalid parameters"}, 400
    webhook = Webhook.query.filter_by(path=request.path).one_or_none()
    if not webhook:
        return {"msg": "The webhook was not configured"}, 404
    if secret:
        if webhook.secret:
            logger.warning(
                "HACKING ATTEMPT: re-write of webhook secret",
                headers=request.headers,
            )
            return {"msg": "Hacking not allowed"}, 400
        webhook.secret = secret
        db.session.add(webhook)
        db.session.commit()

        return {}, 204, {"X-Hook-Secret": secret}

    if not webhook.secret:
        return {"msg": "The webhook does not have a secret"}, 500

    signature = hmac.new(
        webhook.secret.encode("ascii", "ignore"),
        msg=request.data,
        digestmod=hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, request.headers["X-Hook-Signature"]):
        logger.warning(
            "HACKING ATTEMPT: webhook event with non matching signature",
            headers=request.headers,
        )
        return {"msg": "Hacking not allowed"}, 400

    event = Event(webhook=webhook, content=request.json["events"])
    db.session.add(event)
    db.session.commit()
    return {}, 204

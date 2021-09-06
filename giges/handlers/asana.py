import hashlib
import hmac
from typing import Dict, Tuple, Union

import structlog
from connexion import request

from giges.db import db
from giges.models.asana import Event, Project, Webhook

logger = structlog.get_logger(__name__)


def task_webhook(
    project_id: str,
) -> Union[Tuple[Dict, int], Tuple[Dict, int, Dict[str, str]]]:
    """
    Handle incoming webhooks of modified tasks from an asana project.

    :param project_id: the external (asana) ID of the project
    :return: - a tuple with an empty body and the status
             - a tuple with an empty body, the status and the handshake header
    """
    webhook = Webhook.query.filter_by(path=request.path).one_or_none()
    if not webhook:
        return {"msg": "The webhook was not configured"}, 404
    project = Project.query.filter_by(external_id=project_id).one_or_none()
    if not project:
        return {"msg": "The project was not configured"}, 404
    if webhook.project != project:
        return {"msg": "The webhook does not match the targeted project"}, 400
    return handle_webhook(webhook)


def project_webhook() -> Union[
    Tuple[Dict, int], Tuple[Dict, int, Dict[str, str]]
]:
    """
    Handle incoming webooks of new projects from asana.

    :return: - a tuple with an empty body and the status
             - a tuple with an empty body, the status and the handshake header
    """
    webhook = Webhook.query.filter_by(path=request.path).one_or_none()
    if not webhook:
        return {"msg": "The webhook was not configured"}, 404
    return handle_webhook(webhook)


def handle_webhook(
    webhook: Webhook,
) -> Union[Tuple[Dict, int], Tuple[Dict, int, Dict[str, str]]]:
    """
    Handle incoming webhooks from asana.

    When registering a webhook, asana will first send a request with a secret,
    X-Hook-Secret, that we use to verify the authenticity of the rest of the
    webhooks requests using X-Hook-Signature.

    :param webhook: the instance of the webhook in Giges
    :return: - a tuple with an empty body and the status
             - a tuple with an empty body, the status and the handshake header
    """
    secret = request.headers.get("X-Hook-Secret")
    signature = request.headers.get("X-Hook-Signature")

    if not secret and not signature:
        return {"msg": "Invalid parameters"}, 400
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

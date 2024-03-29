import hashlib
import hmac
from typing import Any, Callable, Dict, List, Tuple, Union

import asana
import iso8601
import structlog
from connexion import request
from flask import current_app

from giges.db import db
from giges.models.asana import (
    Event,
    Project,
    ResourceTypeEnum,
    Task,
    TaskChange,
    Webhook,
)

logger = structlog.get_logger(__name__)


def create_client() -> asana.Client:
    """
    Initialize and return an Asana sdk object.

    :return: the asana client itself
    """
    return asana.Client.access_token(current_app.config["ASANA_TOKEN"])


def retrieve_task_information(asana_id: str) -> Dict[str, Any]:
    """
    Contacts Asana and download all the information from a task.

    :param asana_id: the external (Asana) ID of the task
    :return: the dictionary from the JSON parsed information
    """
    client = create_client()
    return client.tasks.find_by_id(asana_id)


def retrieve_section_tasks(asana_id: str) -> List[Dict[str, Any]]:
    """

    :param asana_id: the external (Asana) ID of the section
    :return: the dictionary from the JSON parsed information
    """
    client = create_client()
    return client.get_collection(f"/sections/{asana_id}/tasks", {})


def retrieve_subtasks(asana_id: str) -> List[Dict[str, Any]]:
    """

    :param asana_id: the external (Asana) ID of the task
    :return: the dictionary from the JSON parsed information
    """
    client = create_client()
    return client.get_collection(f"/tasks/{asana_id}/subtasks", {})


def create_task(
    name: str, project_id: str, memberships: List[Dict[str, str]] = None
) -> None:
    """

    :param name: the name of the future task
    :param project_id: the external (Asana) ID of the project
    :param memberships: the list of deep tree position of the task
    """
    parameters: Dict[str, Any] = {
        "name": name,
        "notes": "Giges was here.",
        "projects": [project_id],
    }
    if memberships:
        parameters["memberships"] = memberships
    client = create_client()
    client.tasks.create_in_workspace(
        current_app.config["ASANA_WORKSPACE"],
        parameters,
    )


def update_task(task: Task, asana_task: Dict[str, Any]) -> TaskChange:
    """
    Set the values of a task to the current ones in  Asana.

    :param task: the task to update
    :param asana_task: the current task information in Asana
    :return: the object containing the task changes
    """
    task.completed = asana_task.get("completed")
    if asana_task.get("completed_at"):
        task.completed_at = iso8601.parse_date(asana_task.get("completed_at"))
    task.name = asana_task.get("name")
    task.description = asana_task.get("description")
    if len(asana_task["memberships"]):
        task.section = asana_task["memberships"][0]["section"]["name"]
    task.save_custom_fields(asana_task["custom_fields"])

    task_change = TaskChange(task=task)
    task_change.save_task_changes()

    return task_change


def handle_task_events(
    webhook: Webhook, events: List[Dict[str, Dict]]
) -> None:
    """
    Resolves events from webhooks into tasks and tasks changes.

    :param webhook: the handled webhook
    :param events: the list of events given by Asana
    """
    task_gids = set()
    for event in events:
        task_gids.add(event["resource"]["gid"])

    for task_gid in task_gids:
        task = Task.query.filter_by(external_id=task_gid).one_or_none()
        if task is None:
            task = Task(external_id=task_gid)
        asana_task = retrieve_task_information(task_gid)
        task_change = update_task(task, asana_task)
        db.session.add(task)
        db.session.add(task_change)
    db.session.add(Event(webhook=webhook, content=events))
    db.session.commit()


def handle_customer_workflow(
    webhook: Webhook, events: List[Dict[str, Dict]]
) -> None:
    """
    Resolves events from webhooks into tasks and tasks changes.

    :param webhook: the handled webhook
    :param events: the list of events given by Asana
    """
    task_gids = set()
    for event in events:
        task_gid = None
        # Asana will send the stories with the task directly linked
        # or with the task in the parent, without a known rule
        if event.get("task"):
            task_gid = event["task"]["gid"]
        if task_gid is None:
            if event["parent"]["resource_type"] == ResourceTypeEnum.task:
                task_gid = event["parent"]["gid"]
        if task_gid:
            task_gids.add(task_gid)

    # Get all the tasks from the "Template" section of the "Customer Workflow"
    template_tasks = {
        t["name"]: t for t in retrieve_section_tasks("1201165296613104")
    }

    for task_gid in task_gids:
        asana_task = retrieve_task_information(task_gid)
        template = None
        customer_project = None
        customer_section = None
        for membership in asana_task["memberships"]:
            template = template or template_tasks.get(
                membership["section"]["name"]
            )
            if membership["project"]["name"].startswith("P -"):
                customer_project = membership["project"]["gid"]
                customer_section = membership["section"]["gid"]

        if not template or not customer_project:
            break

        template_subtasks = retrieve_subtasks(template["gid"])
        for subtask in template_subtasks:
            create_task(
                subtask["name"],
                customer_project,
                memberships=[
                    {"project": customer_project, "section": customer_section}
                ],
            )

    db.session.add(Event(webhook=webhook, content=events))
    db.session.commit()


def task_webhook(
    project_id: str,
) -> Union[Tuple[Dict, int], Tuple[Dict, int, Dict[str, str]]]:
    """
    Handle incoming webhooks of modified tasks from an asana project.

    :param project_id: the external (asana) ID of the project
    :return: - a tuple with an empty body and the status
             - a tuple with an empty body, the status and the handshake header
    """
    return handle_webhook(project_id, handle_task_events)


def customer_webhook(
    project_id: str,
) -> Union[Tuple[Dict, int], Tuple[Dict, int, Dict[str, str]]]:
    """
    Handle incoming webhooks of the customer workflow changes.

    :param project_id: the external (asana) ID of the project
    :return: - a tuple with an empty body and the status
             - a tuple with an empty body, the status and the handshake header
    """
    return handle_webhook(project_id, handle_customer_workflow)


def handle_webhook(
    project_id: str, handle_events: Callable
) -> Union[Tuple[Dict, int], Tuple[Dict, int, Dict[str, str]]]:
    """
    Handle the core of incoming webhooks from asana.

    When registering a webhook, asana will first send a request with a secret,
    X-Hook-Secret, that we use to verify the authenticity of the rest of the
    webhooks requests using X-Hook-Signature.

    :param project_id: the external (asana) ID of the project
    :param handle_events: the function to handle the events
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

    if len(request.json["events"]) == 0:
        # Asana periodically ping the endpoint without events
        return {}, 204

    try:
        handle_events(webhook, request.json["events"])
    except KeyError:
        return {"msg": "Incorrect event format"}, 400

    return {}, 204

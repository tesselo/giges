import json
from typing import Dict, Generator, List, Union

import asana
import click
import dateutil
from flask import current_app
from flask.cli import with_appcontext

from giges.db import db
from giges.models.asana import Project, ResourceTypeEnum, Webhook


def create_client() -> asana.Client:
    """
    Initialize and return an Asana sdk object.

    :return: the asana client itself
    """
    return asana.Client.access_token(current_app.config["ASANA_TOKEN"])


def print_response(response: Union[Generator, List, Dict]) -> None:
    """
    Beautifully prints responses from Asana.

    :param response: the raw response from asana, in different formats
    """
    if not isinstance(response, dict):
        response = list(response)
    print(json.dumps(response, indent=4))


@click.group(name="asana", help="Manage asana information from giges")
def asana_cli() -> None:
    """
    Placeholder function to create a CLI
    group in the Giges command line.
    """
    pass


@asana_cli.command(help="List all workspaces in Asana (spoiler, only one)")
@with_appcontext
def list_workspaces() -> None:
    """
    Retrieve and print the list of all the Asana workspaces
    accessible by the token.
    """
    client = create_client()
    print_response(client.workspaces.get_workspaces())


@with_appcontext
def _register_webhook(
    path: str, resource: str, filter: Dict[str, str]
) -> None:
    """
    Register a single webhook in Giges and Asana.

    :param path: the absolute path that Asana will call on events
    :param resource: the external (Asana) ID we want to investigate
    :param filter: the filters to know the Asana objects that we are examining
    """
    client = create_client()
    webhook = Webhook(path=path, resource_type=filter["resource_type"])
    if webhook.resource_type == ResourceTypeEnum.task:
        project = Project.query.filter_by(external_id=resource).one_or_none()
        webhook.project = project
    db.session.add(webhook)
    db.session.commit()

    response = client.webhooks.create(
        resource=resource,
        target=f"{current_app.config['SERVER_BASE_URI']}{path}",
        filters=[filter],
    )
    webhook.external_id = response["gid"]
    db.session.add(webhook)
    db.session.commit()

    print_response(response)


@asana_cli.command(help="Configure webhooks for asana projects")
@with_appcontext
def create_projects_webhook() -> None:
    """
    Register a single projects webhook in Giges and Asana.
    """
    _register_webhook(
        "/asana/projects",
        current_app.config["ASANA_WORKSPACE"],
        {"resource_type": ResourceTypeEnum.project, "action": "added"},
    )


@asana_cli.command(help="Configure a webhook for asana tasks in a project")
@click.argument("project_id", required=True)
@with_appcontext
def create_tasks_webhook(project_id: str) -> None:
    """
    Register a single tasks webhook in Giges and Asana relative to a project

    :param project_id: the external (Asana) ID of the project
    """
    _register_webhook(
        f"/asana/projects/{project_id}",
        project_id,
        {"resource_type": ResourceTypeEnum.task},
    )


@asana_cli.command(help="List currently configured Asana webhooks")
@with_appcontext
def list_webhooks() -> None:
    """
    Retrieve and print the list of all the Asana webhooks
    accessible by the token.
    """

    client = create_client()
    print_response(
        client.webhooks.get_webhooks(
            workspace=current_app.config["ASANA_WORKSPACE"]
        )
    )


@asana_cli.command(help="List all Asana projects")
@with_appcontext
def list_projects() -> None:
    """
    Retrieve and print the list of all the Asana projects
    accessible by the token.
    """
    client = create_client()
    print_response(
        client.projects.find_all(
            workspace=current_app.config["ASANA_WORKSPACE"]
        )
    )


def _is_client_or_workflow(project_name: str) -> bool:
    """
    Determine if the project is client or workflow related.

    :param project_name: the string containing the project name
    """
    return project_name.startswith("P -") or project_name.endswith("Workflow")


@asana_cli.command(help="Add relevant or all Asana projects")
@click.argument("add_all", type=bool, default=False)
@with_appcontext
def add_projects(add_all: bool = False) -> None:
    """
    Add Asana projects to Giges database.

    :param add_all: if True, will add all the projects,
                    if False, will add only clients and workflow projects
    """
    added: int = 0
    client = create_client()
    projects = client.projects.find_all(
        workspace=current_app.config["ASANA_WORKSPACE"]
    )
    for project in projects:
        if add_all or _is_client_or_workflow(project["name"]):
            external_id = project["gid"]
            p = Project.query.filter_by(external_id=external_id).one_or_none()
            if not p:
                project = client.projects.find_by_id(external_id)
                p = Project(
                    external_id=project["gid"],
                    name=project["name"],
                    created_at=dateutil.parser.parse(project["created_at"]),
                    updated_at=dateutil.parser.parse(project["modified_at"]),
                )
                db.session.add(p)
                added += 1
    if added:
        db.session.commit()
        print(f"{added} new projects added")


@asana_cli.command(help="Show all information about a single project")
@click.argument("project_id", required=True)
@with_appcontext
def show_project(project_id: str) -> None:
    """
    Retrieve and print a single Asana project accessible by the token.

    :param project_id: the external (Asana) ID of the project
    """
    client = create_client()
    print_response(client.projects.find_by_id(project_id))


@asana_cli.command(help="Show all information about a single task")
@click.argument("task_id", required=True)
@with_appcontext
def show_task(task_id: str) -> None:
    """
    Retrieve and print a single Asana task accessible by the token.

    :param task_id: the external (Asana) ID of the task
    """
    client = create_client()
    print_response(client.tasks.find_by_id(task_id))


@asana_cli.command(help="Generate Custom field mappings")
@click.argument("project_id", required=True)
@with_appcontext
def generate_custom_field_dicts(project_id: str) -> None:
    """
    Retrieve the custom fields from an Asana project
    and build a dictionary with the mappings that we
    will use to save the information into our database.

    :param project_id: the external (Asana) ID of the project
    """
    client = create_client()
    response = client.projects.find_by_id(project_id)
    custom_fields = {}
    for setting in response.get("custom_field_settings", []):
        field = setting["custom_field"]
        if field["type"] == "enum":
            # Only the enums need mappings
            options = {}
            for option in field.get("enum_options", []):
                options[option["gid"]] = option["name"]
            custom_fields[field["gid"]] = {
                "name": field["name"],
                "options": options,
            }
    print_response(custom_fields)


@asana_cli.command(help="Delete a currently configured Asana webhook")
@click.argument("webhook_id", required=True)
@with_appcontext
def delete_webhook(webhook_id: str) -> None:
    """
    Unregister a Webhook in Asana.

    :param webhook_id: the external (Asana) ID of the webhook
    """
    client = create_client()
    print_response(client.webhooks.delete_by_id(webhook_id))

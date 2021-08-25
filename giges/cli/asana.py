import json
from typing import Generator, List, Union

import asana
import click
from flask import current_app
from flask.cli import with_appcontext

from giges.db import db
from giges.models.asana import ResourceTypeEnum, Webhook


def create_client() -> asana.Client:
    return asana.Client.access_token(current_app.config["ASANA_TOKEN"])


def print_response(response: Union[Generator, List]) -> None:
    if not isinstance(response, dict):
        response = list(response)
    print(json.dumps(response, indent=4))


@click.group(name="asana", help="Manage asana information from giges")
def asana_cli() -> None:
    pass


@asana_cli.command(help="List all workspaces in Asana (spoiler, only one)")
@with_appcontext
def list_workspaces() -> None:
    client = create_client()
    print_response(current_app.config)
    print_response(client.workspaces.get_workspaces())


@asana_cli.command(help="Configure a webhook for the asana projects")
@with_appcontext
def create_projects_webhook() -> None:
    client = create_client()
    path = "/asana/projects"

    webhook = Webhook(path=path, resource_type=ResourceTypeEnum.project)
    db.session.add(webhook)
    db.session.commit()

    response = client.webhooks.create(
        resource=current_app.config["ASANA_WORKSPACE"],
        target=f"{current_app.config['SERVER_BASE_URI']}{path}",
        filters=[{"resource_type": "project"}],
    )

    print_response(response)
    webhook.external_id = response["gid"]
    db.session.add(webhook)
    db.session.commit()


@asana_cli.command(help="List currently configured Asana webhooks")
@with_appcontext
def list_webhooks() -> None:
    client = create_client()
    print_response(
        client.webhooks.get_webhooks(
            workspace=current_app.config["ASANA_WORKSPACE"]
        )
    )


@asana_cli.command(help="List all Asana projects")
@with_appcontext
def list_projects() -> None:
    client = create_client()
    print_response(
        client.projects.find_all(
            workspace=current_app.config["ASANA_WORKSPACE"]
        )
    )


@asana_cli.command(help="Delete a currently configured Asana webhook")
@click.argument("webhook_id", required=True)
@with_appcontext
def delete_webhook(webhook_id: str) -> None:
    client = create_client()
    print_response(client.webhooks.delete_by_id(webhook_id))

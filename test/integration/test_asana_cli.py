import json

import pytest


def test_asana_cli_help(cli_runner):
    result = cli_runner.invoke(args=["asana"])
    assert "Manage asana information from giges" in result.output


@pytest.mark.vcr
def test_asana_cli_list_workspaces(cli_runner):
    result = cli_runner.invoke(args=["asana", "list-workspaces"])

    assert result.exit_code == 0
    assert "name" in result.output
    assert "tesselo.com" in result.output
    assert "resource_type" in result.output


@pytest.mark.vcr
def test_asana_cli_list_projects(cli_runner):
    result = cli_runner.invoke(args=["asana", "list-projects"])

    assert result.exit_code == 0
    projects = json.loads(result.output)
    for project in projects:
        assert project["resource_type"] == "project"


@pytest.mark.vcr
def test_asana_cli_create_projects_webhook(cli_runner):
    result = cli_runner.invoke(args=["asana", "create-projects-webhook"])

    assert result.exit_code == 0
    webhook = json.loads(result.output)
    assert webhook["resource_type"] == "webhook"
    assert webhook["filters"][0]["resource_type"] == "project"
    assert webhook["filters"][0]["action"] == "added"


def test_asana_cli_create_tasks_webhook_without_id(cli_runner):
    result = cli_runner.invoke(args=["asana", "create-tasks-webhook"])

    assert result.exit_code != 0


@pytest.mark.vcr
def test_asana_cli_create_tasks_webhook(cli_runner, project, transactional_db):
    project.external_id = "1200150717156531"
    transactional_db.add(project)
    transactional_db.commit()
    result = cli_runner.invoke(
        args=["asana", "create-tasks-webhook", project.external_id]
    )

    assert result.exit_code == 0
    webhook = json.loads(result.output)
    assert webhook["resource_type"] == "webhook"
    assert webhook["filters"][0]["resource_type"] == "task"


@pytest.mark.vcr
def test_asana_cli_list_webhooks(cli_runner):
    result = cli_runner.invoke(args=["asana", "list-webhooks"])

    assert result.exit_code == 0
    webhooks = json.loads(result.output)
    for webhook in webhooks:
        assert webhook["resource_type"] == "webhook"


def test_asana_cli_delete_webhook_without_id(cli_runner):
    result = cli_runner.invoke(args=["asana", "delete-webhook"])

    assert result.exit_code != 0
    assert "Missing argument" in result.output


@pytest.mark.vcr
def test_asana_cli_delete_webhook(cli_runner):
    result = cli_runner.invoke(
        args=["asana", "delete-webhook", "1200890863508545"]
    )

    assert result.exit_code == 0

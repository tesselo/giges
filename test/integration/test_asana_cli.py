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


@pytest.mark.vcr
def test_asana_cli_add_projects(cli_runner):
    result = cli_runner.invoke(args=["asana", "add-projects"])

    print("holi")
    assert result.exit_code == 0
    assert "new projects added" in result.output


@pytest.mark.vcr
def test_asana_cli_show_project(cli_runner):
    result = cli_runner.invoke(
        args=["asana", "show-project", "1200150717156531"]
    )

    assert result.exit_code == 0
    assert "Frontend Workflow" in result.output


@pytest.mark.vcr
def test_asana_cli_show_task(cli_runner):
    result = cli_runner.invoke(args=["asana", "show-task", "1201046407912294"])

    assert result.exit_code == 0
    assert "webhook subscriptions" in result.output


@pytest.mark.vcr
def test_asana_cli_generate_custom_field_dicts(cli_runner):
    result = cli_runner.invoke(
        args=["asana", "generate-custom-field-dicts", "1200802773613549"]
    )

    assert result.exit_code == 0
    assert "Priority" in result.output
    assert "Timebomb" in result.output

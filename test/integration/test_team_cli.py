from giges.models.team import Team, Tessera


def test_team_cli_help(cli_runner):
    result = cli_runner.invoke(args=["team"])
    assert "Manage team knowledge in giges" in result.output


def test_team_cli_add_team(cli_runner, db_session):
    assert Team.query.count() == 0

    cli_runner.invoke(args=["team", "add-team", "Rocket"])

    assert Team.query.count() == 1
    team = Team.query.first()
    assert team.name == "Rocket"


def test_team_cli_add_tessera(cli_runner, db_session):
    assert Tessera.query.count() == 0

    cli_runner.invoke(
        args=["team", "add-tessera", "Meowth", "asana", "github", "slack"]
    )

    assert Tessera.query.count() == 1
    tessera = Tessera.query.first()

    assert tessera.name == "Meowth"
    assert tessera.asana_id == "asana"
    assert tessera.github_handle == "github"
    assert tessera.slack_id == "slack"


def test_team_cli_add_tessera_to_team(cli_runner, db_session, team, tessera):
    team_name = team.name
    cli_runner.invoke(
        args=["team", "add-tessera-to-team", tessera.id, team.id]
    )
    db_session.add(tessera)
    assert tessera.teams[0].name == team_name


def test_team_cli_remove_tessera_from_team(
    cli_runner, db_session, team, tessera
):
    team.tesseras.append(tessera)

    assert len(tessera.teams) == 1

    result = cli_runner.invoke(
        args=["team", "remove-tessera-from-team", tessera.id, team.id]
    )
    assert result.exit_code == 0, result.output
    db_session.add(tessera)

    assert len(tessera.teams) == 0


def test_team_cli_add_project_to_team(cli_runner, db_session, team, project):
    project_name = project.name

    result = cli_runner.invoke(
        args=["team", "add-project-to-team", project.id, team.id]
    )
    assert result.exit_code == 0, result.output
    db_session.add(team)

    assert team.projects[0].name == project_name


def test_team_cli_remove_project_from_team(
    cli_runner, db_session, team, project
):
    team.projects.append(project)

    assert len(team.projects) == 1
    assert team.projects[0].name == project.name

    result = cli_runner.invoke(
        args=["team", "remove-project-from-team", project.id, team.id]
    )
    assert result.exit_code == 0, result.output
    db_session.add(team)

    assert len(team.projects) == 0

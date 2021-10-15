import click
from flask.cli import with_appcontext

from giges.db import db
from giges.models.asana import Project
from giges.models.team import Team, Tessera
from giges.tasks.asana import daily_stick


@click.group(name="team", help="Manage team knowledge in giges")
def team_cli() -> None:
    """
    Placeholder function to create a CLI
    group in the Giges command line.
    """
    pass


@team_cli.command(help="Add a team to Giges")
@click.argument("name", type=str, required=True)
@with_appcontext
def add_team(name: str) -> None:
    """
    Add amazing teams to Giges database.

    :param name: the *unique* name of the team
    """
    t = Team(name=name)
    db.session.add(t)
    db.session.commit()


@team_cli.command(help="Add a tessera to Giges")
@click.argument("name", type=str, required=True)
@click.argument("asana", type=str, default=None)
@click.argument("github", type=str, default=None)
@click.argument("slack", type=str, default=None)
@with_appcontext
def add_tessera(
    name: str, asana: str = None, github: str = None, slack: str = None
) -> None:
    """
    Add wonderful humans to Giges database.

    :param name: the *unique* name of the team
    :param asana: the string with numbers that identify the person in Asana
    :param github: the username in github of the human
    :param slack: the string that starts with U to identify the person in slack
    """
    t = Tessera(
        name=name, asana_id=asana, github_handle=github, slack_id=slack
    )
    db.session.add(t)
    db.session.commit()


@team_cli.command(help="Add a tessera to a team")
@click.argument("tessera_id", type=str, required=True)
@click.argument("team_id", type=str, required=True)
@with_appcontext
def add_tessera_to_team(tessera_id: str, team_id: str) -> None:
    """
    Add a tessera to a team
    :param tessera_id: the giges UUID for this tessera
    :param team_id: the giges UUID for the team
    """
    tessera = Tessera.query.get(tessera_id)
    team = Team.query.get(team_id)
    team.tesseras.append(tessera)
    db.session.add(team)
    db.session.commit()


@team_cli.command(help="Kicks a tessera from a team")
@click.argument("tessera_id", type=str, required=True)
@click.argument("team_id", type=str, required=True)
@with_appcontext
def remove_tessera_from_team(tessera_id: str, team_id: str) -> None:
    """
    Kicks a tessera from a team
    :param tessera_id: the giges UUID for this tessera
    :param team_id: the giges UUID for the team
    """
    tessera = Team.query.get(tessera_id)
    team = Team(name=team_id)
    team.tesseras.remove(tessera)
    db.session.add(team)
    db.session.commit()


@team_cli.command(help="Add a project to a team")
@click.argument("project_id", type=str, required=True)
@click.argument("team_id", type=str, required=True)
@with_appcontext
def add_project_to_team(project_id: str, team_id: str) -> None:
    """
    Add a project (asana board) to a team
    :param project_id: the giges UUID for the project
    :param team_id: the giges UUID for the team
    """
    project = Project.query.get(project_id)
    team = Team.query.get(team_id)
    team.projects.append(project)
    db.session.add(team)
    db.session.commit()


@team_cli.command(help="Removes a project from a team")
@click.argument("tessera_id", type=str, required=True)
@click.argument("team_id", type=str, required=True)
@with_appcontext
def remove_project_from_team(project_id: str, team_id: str) -> None:
    """
    Removes a project from a team
    :param project_id: the giges UUID for the project
    :param team_id: the giges UUID for the team
    """
    project = Project.query.get(project_id)
    team = Team.query.get(team_id)
    team.tesseras.remove(project)
    db.session.add(team)
    db.session.commit()


@team_cli.command(help="Pokes the team")
@click.argument("team_id", type=str, required=True)
@with_appcontext
def stick(team_id: str) -> None:
    daily_stick(team_id)

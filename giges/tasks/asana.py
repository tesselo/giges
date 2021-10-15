from typing import Dict, List

import asana
from flask import current_app
from zappa.asynchronous import task

from giges.models.team import Team
from giges.slack import SlackClient


def _add_ds_class_item(custom_field: Dict[str, str]) -> str:
    """
    Returns the slack representation for a Data Science item.

    :param custom_field: the unprocessed value from asana API
    :return: a string with an emoji and the name
    """
    return f':large_green_square: {custom_field["name"]}'


def _add_pf_class_item(custom_field: Dict[str, str]) -> str:
    """
    Returns the slack representation for a Platform item.

    :param custom_field: the unprocessed value from asana API
    :return: a string with an emoji and the name
    """
    return f':large_blue_square: {custom_field["name"]}'


def _add_section(memberships: List[Dict], team_projects: List[str]) -> str:
    """
    Returns the name of the section of the workflow project
    the selected task is currently on.

    :param memberships: the memberships response from asana API
    :param team_projects: a list of the ids of the team projects
    :return: a string with the name of the section
    """
    section = ""
    for membership in memberships:
        if membership.get("project"):
            if membership["project"]["gid"] in team_projects:
                section = membership["section"]["name"]

    return section


def _add_class_of_service(custom_field: Dict[str, str]) -> str:
    """
    Returns the slack representation for the class of service of an item.

    :param custom_field: the unprocessed value from asana API
    :return: a string with an emoji
    """
    emojis = {
        "1200760323624685": ":rocket:",
        "1200760323624695": ":bomb:",
        "1200760323630880": ":black_square_button:",
        "1200760323631982": ":brain:",
    }

    return f'{emojis.get(custom_field["gid"], ":chipmunk:")} '


@task
def daily_stick(team_id: str = None) -> None:
    """
    For all the projects that belongs to a team:
        - list all the current tasks
        - assigned to each person in the team
        - annoy the sufficient amount

    :param team_id: the giges UUID of the team
    """
    asana_client = asana.Client.access_token(current_app.config["ASANA_TOKEN"])
    slack_client = SlackClient()
    workspace_id = current_app.config["ASANA_WORKSPACE"]

    if team_id is None:
        # Search for the Tech team by default
        team = Team.query.filter_by(name="Tech").one_or_none()
    else:
        team = Team.query.get(team_id)
    projects_ids = [p.external_id for p in team.projects]

    for human in team.tesseras:
        message = f"<@{human.slack_id}|{human.name}> :robot_face: :qoobe_hi:"
        tasks = asana_client.tasks.search_tasks_for_workspace(
            workspace_gid=workspace_id,
            params={
                "assignee.any": human.asana_id,
                "projects.any": ",".join(projects_ids),
                "completed": False,
                "is_subtask": False,
                # 1200200605652838 = In Progress
                "custom_fields.1200200605652836.value": 1200200605652838,
            },
            options={"fields": "followers,assignee", "opt_pretty": True},
        )
        for t in tasks:
            task = asana_client.tasks.find_by_id(t["gid"])
            message += "\n\t -  <https://app.asana.com/0/"
            message += f"{workspace_id}/{task['gid']}/f|{task['name']}> \t"

            fields = {
                "section": _add_section(task["memberships"], projects_ids)
            }
            for field in task["custom_fields"]:
                if field["gid"] == "1200760323623705":
                    fields["class"] = _add_class_of_service(
                        field["enum_value"]
                    )
                elif (
                    field["gid"] == "1200760343663992" and field["enum_value"]
                ):
                    fields["item"] = _add_ds_class_item(field["enum_value"])
                elif (
                    field["gid"] == "1200765868551790" and field["enum_value"]
                ):
                    fields["item"] = _add_pf_class_item(field["enum_value"])
            message += f"{fields.get('class', ':memo:')} "
            message += f"{fields.get('section', ':fairy:')} "
            message += f"{fields.get('item', ':dragon:')}"

        message += "\n:speech_balloon: -> :thread:\n"
        slack_client.send_to_road_blocks(message)

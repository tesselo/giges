from sqlalchemy import CHAR, ForeignKey, String
from sqlalchemy.orm import relationship

from giges.db import db
from giges.models.mixins import UUIDMixin

team_tessera_association = db.Table(
    "team_tessera_association",
    db.Model.metadata,
    db.Column(
        "team_id", CHAR(36), ForeignKey("team.id", name="team_tessera_team_fk")
    ),
    db.Column(
        "tessera_id",
        CHAR(36),
        ForeignKey("tessera.id", name="team_tessera_tessera_fk"),
    ),
)

team_project_association = db.Table(
    "team_project_association",
    db.Model.metadata,
    db.Column(
        "team_id", CHAR(36), ForeignKey("team.id", name="team_project_team_fk")
    ),
    db.Column(
        "project_id",
        CHAR(36),
        ForeignKey("asana_project.id", name="team_project_project_fk"),
    ),
)


class Team(db.Model, UUIDMixin):

    name = db.Column(
        String, nullable=False, unique=True, index=True, doc="Name of the team"
    )

    tesseras = relationship(
        "Tessera", secondary=team_tessera_association, back_populates="teams"
    )
    projects = relationship("Project", secondary=team_project_association)
    rituals = relationship("Ritual")


class Tessera(db.Model, UUIDMixin):

    name = db.Column(
        String, nullable=False, index=True, doc="Name of the human"
    )
    asana_id = db.Column(
        String, nullable=False, index=True, doc="Asana ID of the tessera"
    )
    github_handle = db.Column(
        String,
        nullable=False,
        index=True,
        doc="User name in Github of this human",
    )
    slack_id = db.Column(
        String, nullable=False, index=True, doc="Slack ID of the tessera"
    )

    teams = relationship(
        "Team", secondary=team_tessera_association, back_populates="tesseras"
    )

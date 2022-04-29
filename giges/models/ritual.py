from sqlalchemy import CHAR, ForeignKey, String
from sqlalchemy.orm import relationship

from giges.db import db
from giges.models.mixins import UUIDMixin


class Ritual(db.Model, UUIDMixin):

    name = db.Column(
        String,
        nullable=False,
        unique=True,
        index=True,
        doc="Name of the ritual",
    )
    team_id = db.Column(
        CHAR(36),
        ForeignKey(
            "team.id",
            deferrable=True,
            initially="DEFERRED",
            name="ritual_team_fk",
        ),
    )

    logs_url = db.Column(
        String,
        nullable=True,
        index=True,
        doc="The Bahamut section for the logs",
    )
    meeting_url = db.Column(
        String,
        nullable=True,
        index=False,
        doc="The URL for the virtual meeting place",
    )
    team = relationship("Team", back_populates="rituals")

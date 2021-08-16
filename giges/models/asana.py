import enum

from sqlalchemy import CHAR, JSON, TIMESTAMP, Column, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from ..db import db
from .mixins import UUIDMixin


class ResourceTypeEnum(str, enum.Enum):
    custom_field = "custom_field"
    enum_option = "enum_option"
    project = "project"
    task = "task"
    webhook = "webhook"
    workspace = "workspace"


class Project(db.Model, UUIDMixin):
    __tablename__ = "asana_project"

    external_id = db.Column(
        String,
        nullable=False,
        index=True,
        doc="The ID of the Project in Asana",
    )
    name = db.Column(
        String, nullable=False, index=True, doc="Name of the project"
    )
    created_at = Column(
        TIMESTAMP,
        nullable=False,
        doc="When the project was created in Asana",
    )
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        doc="When the project was modified in Asana",
    )


class Webhook(db.Model, UUIDMixin):
    __tablename__ = "asana_webhook"

    external_id = db.Column(
        String,
        index=True,
        doc="The ID of the Webhook in Asana",
    )
    path = db.Column(
        String,
        nullable=False,
        index=True,
        doc="The base path where we receive this webhook",
    )
    resource_type = db.Column(
        Enum(ResourceTypeEnum, name="resource_type_enum"),
        doc="Resource type configured to trigger events",
    )
    secret = db.Column(
        String,
        doc="Secret used to verify the hash of received events",
    )


class Event(db.Model, UUIDMixin):
    __tablename__ = "asana_event"

    webhook_id = db.Column(
        CHAR(36),
        ForeignKey(
            "asana_webhook.id",
            deferrable=True,
            initially="DEFERRED",
            name="asana_event_webhook_fk",
        ),
    )

    content = db.Column(
        JSON, doc="The binary JSON content of the received event"
    )

    webhook = relationship("Webhook")

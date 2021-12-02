import enum
from typing import Dict, List

from sqlalchemy import (
    CHAR,
    JSON,
    TIMESTAMP,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship

from ..db import db
from ..settings import asana_fields
from .mixins import TimestampMixin, UUIDMixin


class ResourceTypeEnum(str, enum.Enum):
    custom_field = "custom_field"
    enum_option = "enum_option"
    project = "project"
    task = "task"
    story = "story"
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
    created_at = db.Column(
        TIMESTAMP,
        nullable=False,
        doc="When the project was created in Asana",
    )
    updated_at = db.Column(
        TIMESTAMP,
        nullable=False,
        doc="When the project was modified in Asana",
    )


class Webhook(db.Model, UUIDMixin):
    __tablename__ = "asana_webhook"

    project_id = db.Column(
        CHAR(36),
        ForeignKey(
            "asana_project.id",
            deferrable=True,
            initially="DEFERRED",
            name="asana_webhook_project_fk",
        ),
    )
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

    project = relationship("Project")


class Task(db.Model, UUIDMixin, TimestampMixin):
    __tablename__ = "asana_task"

    external_id = db.Column(
        String,
        index=True,
        doc="The ID of the Task in Asana",
    )

    name = db.Column(
        String, nullable=False, index=True, doc="Name of the task"
    )
    description = db.Column(String, index=True, doc="Description of the task")
    completed = db.Column(Boolean)
    completed_at = db.Column(DateTime)

    class_of_service = db.Column(String)
    task_progress = db.Column(String)
    item_category = db.Column(String)
    related_service = db.Column(String)
    section = db.Column(String)

    def save_custom_fields(self, custom_fields: List[Dict]) -> None:
        """
        Mapping between the Asana custom fields and the information we want
        to save and track into the database.

        :param custom_fields: dict from Asana show task response
        :return: Nope
        """
        for field in custom_fields:
            field_id = field.get("gid")
            if field_id in asana_fields.keys():
                if field.get("enum_value"):
                    value = asana_fields[field_id]["options"][
                        field["enum_value"]["gid"]
                    ]
                    setattr(self, asana_fields[field_id]["column"], value)


class TaskChange(db.Model, UUIDMixin, TimestampMixin):
    __tablename__ = "asana_task_change"

    task_id = db.Column(
        CHAR(36),
        ForeignKey(
            "asana_task.id",
            deferrable=True,
            initially="DEFERRED",
            name="asana_task_change_task_fk",
        ),
    )

    class_of_service = db.Column(String)
    task_progress = db.Column(String)
    item_category = db.Column(String)
    related_service = db.Column(String)
    section = db.Column(String)

    task = relationship("Task")

    def save_task_changes(self) -> None:
        """
        Inspect the sqlalchemy object of a task to determine
        and save the columns that changed.

        :return: Nein
        """
        from sqlalchemy import inspect
        from sqlalchemy.orm import class_mapper

        inspected = inspect(self.task)
        attrs = class_mapper(self.task.__class__).column_attrs
        for attr in attrs:
            if hasattr(self, attr.key) and attr.key != "id":
                hist = getattr(inspected.attrs, attr.key).history
                if hist.has_changes():
                    setattr(self, attr.key, getattr(self.task, attr.key))


class Event(db.Model, UUIDMixin, TimestampMixin):
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

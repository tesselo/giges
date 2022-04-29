from factory import Faker, LazyAttribute, SubFactory
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyText
from faker.providers import date_time

from giges.db import db
from giges.models.asana import Event, Project, ResourceTypeEnum, Webhook
from giges.models.ritual import Ritual
from giges.models.team import Team

Faker.add_provider(date_time)


class ProjectFactory(SQLAlchemyModelFactory):
    external_id = FuzzyText(chars="0123456789")
    name = FuzzyText()
    created_at = Faker("date_between", start_date="-60d", end_date="-1d")
    updated_at = Faker("date_between", start_date="-50d", end_date="now")

    class Meta:
        model = Project
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"


class WebhookFactory(SQLAlchemyModelFactory):
    project = SubFactory(ProjectFactory)
    external_id = FuzzyText(chars="0123456789")
    path = LazyAttribute(lambda w: f"/asana/projects/{w.project.external_id}")
    resource_type = FuzzyChoice(choices=ResourceTypeEnum)
    secret = FuzzyText()

    class Meta:
        model = Webhook
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"


class EventFactory(SQLAlchemyModelFactory):
    webhook = SubFactory(WebhookFactory)
    content = {FuzzyText(): FuzzyText()}

    class Meta:
        model = Event
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"


class TeamFactory(SQLAlchemyModelFactory):
    name = FuzzyText()

    class Meta:
        model = Team
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"


class RitualFactory(SQLAlchemyModelFactory):
    name = FuzzyText()
    team = SubFactory(TeamFactory)
    logs_url = FuzzyText()
    meeting_url = FuzzyText()

    class Meta:
        model = Ritual
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

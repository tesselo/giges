from factory import Faker, SubFactory
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyText
from faker.providers import date_time

from giges.db import db
from giges.models.asana import Event, Project, ResourceTypeEnum, Webhook

Faker.add_provider(date_time)


class WebhookFactory(SQLAlchemyModelFactory):
    external_id = FuzzyText(chars="0123456789")
    path = "/asana/projects"
    resource_type = FuzzyChoice(choices=ResourceTypeEnum)
    secret = FuzzyText()

    class Meta:
        model = Webhook
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"


class ProjectFactory(SQLAlchemyModelFactory):
    external_id = FuzzyText(chars="0123456789")
    name = FuzzyText()
    created_at = Faker("date_between", start_date="-60d", end_date="-1d")
    updated_at = Faker("date_between", start_date="-50d", end_date="now")

    class Meta:
        model = Project
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"


class EventFactory(SQLAlchemyModelFactory):
    webhook = SubFactory(WebhookFactory)
    content = {FuzzyText(): FuzzyText()}

    class Meta:
        model = Event
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

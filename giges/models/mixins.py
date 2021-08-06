import uuid

from sqlalchemy import Column
from sqlalchemy.types import CHAR


class UUIDMixin:
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

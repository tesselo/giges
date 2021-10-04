import uuid
from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP, Column
from sqlalchemy.types import CHAR


def _utc_now() -> datetime:
    """
    Now is more now when it is coming form the UTC.

    :return: the current instant datetime in UTC
    """
    return datetime.now(tz=timezone.utc)


class UUIDMixin:
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))


class TimestampMixin:
    created_at = Column(
        TIMESTAMP(timezone=True),
        default=_utc_now,
        server_onupdate=None,
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        default=_utc_now,
        onupdate=_utc_now,
        nullable=False,
    )

"""Add project to webhooks

Revision ID: 2bb66a995457
Revises: a6a81fe8dbf0
Create Date: 2021-09-02 16:21:19.436037

"""
import sqlalchemy as sa
from alembic import op

from migrations.utils import is_sqlite

# revision identifiers, used by Alembic.
revision = "2bb66a995457"
down_revision = "a6a81fe8dbf0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if is_sqlite():
        with op.batch_alter_table("asana_event", schema=None) as batch_op:
            batch_op.drop_constraint(
                "asana_event_webhook_fk", type_="foreignkey"
            )
            batch_op.create_foreign_key(
                "asana_event_webhook_fk",
                "asana_webhook",
                ["webhook_id"],
                ["id"],
                initially="DEFERRED",
                deferrable=True,
            )

        with op.batch_alter_table("asana_webhook", schema=None) as batch_op:
            batch_op.add_column(
                sa.Column("project_id", sa.CHAR(length=36), nullable=True)
            )
            batch_op.create_foreign_key(
                "asana_webhook_project_fk",
                "asana_project",
                ["project_id"],
                ["id"],
                initially="DEFERRED",
                deferrable=True,
            )
    else:
        op.drop_constraint(
            "asana_event_webhook_fk", "asana_event", type_="foreignkey"
        )
        op.create_foreign_key(
            "asana_event_webhook_fk",
            "asana_event",
            "asana_webhook",
            ["webhook_id"],
            ["id"],
            initially="DEFERRED",
            deferrable=True,
        )
        op.add_column(
            "asana_webhook",
            sa.Column("project_id", sa.CHAR(length=36), nullable=True),
        )
        op.create_foreign_key(
            "asana_webhook_project_fk",
            "asana_webhook",
            "asana_project",
            ["project_id"],
            ["id"],
            initially="DEFERRED",
            deferrable=True,
        )


def downgrade() -> None:
    if is_sqlite():
        with op.batch_alter_table("asana_webhook", schema=None) as batch_op:
            batch_op.drop_constraint(
                "asana_webhook_project_fk", type_="foreignkey"
            )
            batch_op.drop_column("project_id")

        with op.batch_alter_table("asana_event", schema=None) as batch_op:
            batch_op.drop_constraint(
                "asana_event_webhook_fk", type_="foreignkey"
            )
            batch_op.create_foreign_key(
                "asana_event_webhook_fk",
                "asana_webhook",
                ["webhook_id"],
                ["id"],
            )

    else:
        op.drop_constraint(
            "asana_webhook_project_fk", "asana_webhook", type_="foreignkey"
        )
        op.drop_column("asana_webhook", "project_id")
        op.drop_constraint(
            "asana_event_webhook_fk", "asana_event", type_="foreignkey"
        )
        op.create_foreign_key(
            "asana_event_webhook_fk",
            "asana_event",
            "asana_webhook",
            ["webhook_id"],
            ["id"],
        )

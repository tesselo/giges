"""Task and TaskChange models

Revision ID: 089ccde49d20
Revises: 2bb66a995457
Create Date: 2021-10-04 17:00:46.802955

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "089ccde49d20"
down_revision = "2bb66a995457"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "asana_task",
        sa.Column("id", sa.CHAR(length=36), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("class_of_service", sa.String(), nullable=True),
        sa.Column("task_progress", sa.String(), nullable=True),
        sa.Column("item_category", sa.String(), nullable=True),
        sa.Column("related_service", sa.String(), nullable=True),
        sa.Column("section", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "asana_task_change",
        sa.Column("id", sa.CHAR(length=36), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("task_id", sa.CHAR(length=36), nullable=True),
        sa.Column("class_of_service", sa.String(), nullable=True),
        sa.Column("task_progress", sa.String(), nullable=True),
        sa.Column("item_category", sa.String(), nullable=True),
        sa.Column("related_service", sa.String(), nullable=True),
        sa.Column("section", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["asana_task.id"],
            name="asana_task_change_task_fk",
            initially="DEFERRED",
            deferrable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_asana_task_description"),
        "asana_task",
        ["description"],
        unique=False,
    )
    op.create_index(
        op.f("ix_asana_task_external_id"),
        "asana_task",
        ["external_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_asana_task_name"), "asana_task", ["name"], unique=False
    )
    op.add_column(
        "asana_event",
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )
    op.add_column(
        "asana_event",
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("asana_event", "updated_at")
    op.drop_column("asana_event", "created_at")
    op.drop_table("asana_task_change")
    op.drop_index(op.f("ix_asana_task_name"), table_name="asana_task")
    op.drop_index(op.f("ix_asana_task_external_id"), table_name="asana_task")
    op.drop_index(op.f("ix_asana_task_description"), table_name="asana_task")
    op.drop_table("asana_task")

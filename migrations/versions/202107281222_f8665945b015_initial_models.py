"""Initial models

Revision ID: f8665945b015
Revises:
Create Date: 2021-07-28 12:22:00.002237

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f8665945b015"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "asana_project",
        sa.Column("id", sa.CHAR(length=36), nullable=False),
        sa.Column("external_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_asana_project_external_id"),
        "asana_project",
        ["external_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_asana_project_name"), "asana_project", ["name"], unique=False
    )
    op.create_table(
        "asana_webhook",
        sa.Column("id", sa.CHAR(length=36), nullable=False),
        sa.Column("external_id", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column(
            "resource_type",
            sa.Enum(
                "custom_field",
                "enum_option",
                "project",
                "task",
                "webhook",
                "workspace",
                name="resource_type_enum",
            ),
            nullable=True,
        ),
        sa.Column("secret", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_asana_webhook_external_id"),
        "asana_webhook",
        ["external_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_asana_webhook_path"), "asana_webhook", ["path"], unique=False
    )
    op.create_table(
        "asana_event",
        sa.Column("id", sa.CHAR(length=36), nullable=False),
        sa.Column("webhook_id", sa.CHAR(length=36), nullable=True),
        sa.Column("content", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["webhook_id"],
            ["asana_webhook.id"],
            name="asana_event_webhook_fk",
            initially="DEFERRED",
            deferrable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("asana_event")
    op.drop_index(op.f("ix_asana_webhook_path"), table_name="asana_webhook")
    op.drop_index(
        op.f("ix_asana_webhook_external_id"), table_name="asana_webhook"
    )
    op.drop_table("asana_webhook")
    op.drop_index(op.f("ix_asana_project_name"), table_name="asana_project")
    op.drop_index(
        op.f("ix_asana_project_external_id"), table_name="asana_project"
    )
    op.drop_table("asana_project")
    # ### end Alembic commands ###
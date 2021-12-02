"""Add story to resource type enum

Revision ID: 98abb3966af0
Revises: 20c506662a93
Create Date: 2021-11-23 17:16:01.116120

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "98abb3966af0"
down_revision = "20c506662a93"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.sync_enum_values(
        "public",
        "resource_type_enum",
        [
            "custom_field",
            "enum_option",
            "project",
            "task",
            "webhook",
            "workspace",
        ],
        [
            "custom_field",
            "enum_option",
            "project",
            "task",
            "story",
            "webhook",
            "workspace",
        ],
    )


def downgrade() -> None:
    op.sync_enum_values(
        "public",
        "resource_type_enum",
        [
            "custom_field",
            "enum_option",
            "project",
            "task",
            "story",
            "webhook",
            "workspace",
        ],
        [
            "custom_field",
            "enum_option",
            "project",
            "task",
            "webhook",
            "workspace",
        ],
    )

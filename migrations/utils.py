from alembic import context

config = context.config


def is_sqlite() -> bool:
    """We need to know if we are on SQLite on every migration.

    Why? Good question, but it is risky to know the answer

    SQLite has almost no support for the ALTER SQL statement
    And that is not good for migrations, so sqlalchemy has a hack-mode
    that will "move and copy" all the data for each modified table
    for each of the migrations applied. And we don't want to do this
    on our production environments, but it is still handy to have
    SQLite on our local machines and in the CI.

    Visit this link to learn more about this Batch mode:
    https://alembic.sqlalchemy.org/en/latest/batch.html

    :return: bool
    """
    return config.get_main_option("sqlalchemy.url").startswith("sqlite:///")

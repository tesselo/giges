import sys

import flask.cli

from .app import create_flask_app


def main() -> None:
    flask.cli.FlaskGroup(create_app=create_flask_app).main(
        args=sys.argv[1:], prog_name=f"python -m {__package__}"
    )


if __name__ == "__main__":
    main()

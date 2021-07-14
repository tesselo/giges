from giges.app import create_connexion_app

app = create_connexion_app()


def main() -> None:
    app.run(port=8080)


if __name__ == "__main__":
    main()

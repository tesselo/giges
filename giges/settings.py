import os
from pathlib import Path


class BaseSettings:
    APP_NAME = os.getenv("GIGES_APP_NAME", "giges")
    APP_VERSION = os.getenv("APP_VERSION", "latest")

    ENVIRONMENT = ""
    DEBUG = os.getenv("GIGES_DEBUG", "0") == "1"

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("GIGES_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionSettings(BaseSettings):
    ENVIRONMENT = "production"


class StagingSettings(BaseSettings):
    ENVIRONMENT = "staging"


class DevelopmentSettings(BaseSettings):
    ENVIRONMENT = "development"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{Path(__file__).parents[1]}/development.db"
    )


class TestingSettings(BaseSettings):
    ENVIRONMENT = "testing"
    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{Path(__file__).parents[1]}/testing.db"
    )

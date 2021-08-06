import os


class BaseSettings:
    APP_NAME = os.getenv("GIGES_APP_NAME", "giges")
    APP_VERSION = os.getenv("APP_VERSION", "latest")

    ENVIRONMENT = ""
    DEBUG = os.getenv("GIGES_DEBUG", "0") == "1"


class ProductionSettings(BaseSettings):
    ENVIRONMENT = "production"


class StagingSettings(BaseSettings):
    ENVIRONMENT = "staging"


class DevelopmentSettings(BaseSettings):
    ENVIRONMENT = "development"
    DEBUG = True


class TestingSettings(BaseSettings):
    ENVIRONMENT = "testing"

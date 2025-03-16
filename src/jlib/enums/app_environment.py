from enum import Enum


class AppEnvironmentEnum(Enum):
    TEST = "test"
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"

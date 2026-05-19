# pylint: disable=invalid-name
import os
from pathlib import Path
from dataclasses import dataclass


def load_env_file(filepath: str) -> None:
    env_path = Path(filepath)
    if not env_path.exists():
        return

    with env_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                # Keep values already injected by the environment (e.g. Docker/K8s).
                os.environ.setdefault(key, value)


load_env_file(".env")


@dataclass(frozen=True)
class AuthConfig:
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    PASSWORD_SALT: str = os.environ.get("PASSWORD_SALT")


@dataclass(frozen=True)
class DBConfig:
    HOST: str = os.environ.get("DB_HOST")
    USERNAME: str = os.environ.get("DB_USERNAME")
    PASSWORD: str = os.environ.get("DB_PASSWORD")
    PORT: str = os.environ.get("DB_PORT")
    DATABASE: str = os.environ.get("DB_DATABASE")


@dataclass(frozen=True)
class RedisConfig:
    HOST: str = os.environ.get("REDIS_HOST")
    PASSWORD: str = os.environ.get("REDIS_PASSWORD")
    PORT: str = os.environ.get("REDIS_PORT")


@dataclass(frozen=True)
class SlaveDBConfig:
    HOST: str = os.environ.get("DB_HOST")
    USERNAME: str = os.environ.get("DB_USERNAME")
    PASSWORD: str = os.environ.get("DB_PASSWORD")
    PORT: str = os.environ.get("DB_PORT")
    DATABASE: str = os.environ.get("DB_DATABASE")


@dataclass(frozen=True)
class OtherConfig:
    APP_ENV: str = os.environ.get("APP_ENV")
    HEADER_PREFIX: str = os.environ.get("HEADER_PREFIX")
    ALLOW_ORIGIN: str = os.environ.get("ALLOW_ORIGIN")
    TIMEZONE: str = os.environ.get("TIMEZONE")
    DATA_EXPORT_LIMIT: str = os.environ.get("DATA_EXPORT_LIMIT")


@dataclass(frozen=True)
class Config:
    AUTH: AuthConfig = AuthConfig()
    DB: DBConfig = DBConfig()
    REDIS: RedisConfig = RedisConfig()
    SLAVE_DB: SlaveDBConfig = SlaveDBConfig()
    OTHER: OtherConfig = OtherConfig()


CONFIG = Config()

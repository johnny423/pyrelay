from os import environ

from pydantic import AnyUrl, BaseModel


class RelaySettings(BaseModel):
    ASYNC_SQLALCHEMY_DATABASE_URI: AnyUrl = "sqlite+aiosqlite:///data.db"  # type: ignore
    SQLALCHEMY_DATABASE_URI: AnyUrl = "sqlite:///data.db"  # type: ignore


settings = RelaySettings.parse_obj(environ)

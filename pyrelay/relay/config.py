from pydantic import AnyUrl, BaseModel


class RelaySettings(BaseModel):
    ASYNC_SQLALCHEMY_DATABASE_URI: AnyUrl = "sqlite+aiosqlite:///data.db"
    SQLALCHEMY_DATABASE_URI: AnyUrl = "sqlite:///data.db"


settings = RelaySettings()

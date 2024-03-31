from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class BotSettings(BaseModel):
    name: str
    token: str


class DBSettings(BaseModel):
    host: str
    port: int
    name: str
    user: str
    password: str


class RedisSettings(BaseModel):
    host: str
    port: int
    db: int
    cache_expires: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__"
    )

    bot: BotSettings
    db: DBSettings
    redis: RedisSettings

    logging_level: str
    email_support: str
    template_link: str
    debug: bool


config = Settings()

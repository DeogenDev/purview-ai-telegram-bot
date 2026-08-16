"""Настройки приложения"""

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings


class BotConfig(BaseModel):
    token: str
    admin_id: int
    managers: list[int]

    @field_validator("managers")
    def validate_managers(cls, value):
        if isinstance(value, int):
            return [int(v.strip()) for v in value.split(",")]
        return value


class ToApisConfig(BaseModel):
    api_key: str
    base_url: str = "https://toapis.com"
    image_model: str = "gemini-3-pro-image-preview"


class Config(BaseSettings):
    bot: BotConfig
    toapis: ToApisConfig

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


conf = Config()

"""Настройки приложения"""

from enum import Enum

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings


class TypeMedia(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class BotConfig(BaseModel):
    token: str
    admin_id: int
    web_app_url: str
    managers: list[int]

    @field_validator("managers")
    def validate_managers(cls, value):
        if isinstance(value, int):
            return [int(v.strip()) for v in value.split(",")]
        return value


class ReplicateConfig(BaseModel):
    api_key: str
    video_model: str
    image_model: str
    remove_background_model: str
    add_color_model: str


class Config(BaseSettings):
    bot: BotConfig
    replicate: ReplicateConfig

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


conf = Config()

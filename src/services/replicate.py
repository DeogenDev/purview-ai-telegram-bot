"""Сервис Replicate"""

from replicate.client import Client
from pydantic import BaseModel

from typing import Union

from shared import conf


class VideoRequest(BaseModel):
    model: str = conf.replicate.video_model
    mode: str = "standard"
    prompt: str
    start_image: str


class ImageRequest(BaseModel):
    model: str = conf.replicate.image_model
    prompt: str
    output_format: str = "png"
    image_input: list[str]


class RemoveBackgroundRequest(BaseModel):
    model: str = conf.replicate.remove_background_model
    image: str


class AddColorRequest(BaseModel):
    model: str = conf.replicate.add_color_model
    image: str
    model_size: str = "large"


class ReplicateService:
    def __init__(self, api_key: str) -> None:
        self._client = Client(api_token=api_key)

    async def generate(
        self,
        request: Union[
            VideoRequest, ImageRequest, RemoveBackgroundRequest, AddColorRequest
        ],
    ) -> str:
        output = await self._client.async_run(
            request.model,
            input=request.model_dump(),
        )
        return output


replicate_service = ReplicateService(api_key=conf.replicate.api_key)

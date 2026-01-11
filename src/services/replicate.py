"""Сервис Replicate"""

from replicate.client import Client
from pydantic import BaseModel

from typing import Union

from src.shared import conf


class VideoRequest(BaseModel):
    model: str = conf.replicate.video_model
    resolution: str = "720p"
    prompt: str
    image: str


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


class UpscaleImageRequest(BaseModel):
    model: str = conf.replicate.upscale_image_model
    image: str
    scale: float = 5.0
    face_enhance: bool = True


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
            params={
                "wait": True,
                "stream": False,
            },
        )
        return output


replicate_service = ReplicateService(api_key=conf.replicate.api_key)

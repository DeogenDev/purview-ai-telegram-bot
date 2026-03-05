"""Сервис Replicate"""

import logging

from replicate.client import Client
from pydantic import BaseModel

from typing import Union

from src.shared import conf

logger = logging.getLogger(__name__)


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
        self._client = Client(api_token=api_key, timeout=180)

    async def generate(
        self,
        request: Union[
            VideoRequest, ImageRequest, RemoveBackgroundRequest, AddColorRequest
        ],
    ) -> str:
        try:
            prediction = await self._client.predictions.async_create(
                request.model,
                input=request.model_dump(),
                stream=True,
                wait=True,
            )
            async for event in prediction.async_stream():
                if event.event == "logs":
                    logger.info(f"Лог: {event.data.strip()}")

            await prediction.async_wait() 
            logger.info(f"Финальный стейт: {prediction.status}") # Проверьте статус тут
            logger.info(f"Результат: {prediction.output}")

            if not prediction.output:
                raise Exception("Нет результата")
            return prediction.output
        except Exception as e:
            raise Exception(f"Ошибка генерации: {prediction.error}")

replicate_service = ReplicateService(api_key=conf.replicate.api_key)

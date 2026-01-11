"""Сервисы приложения"""

from .replicate import (
    replicate_service,
    VideoRequest,
    RemoveBackgroundRequest,
    ImageRequest,
    AddColorRequest,
    UpscaleImageRequest,
)

__all__ = (
    "replicate_service",
    "VideoRequest",
    "RemoveBackgroundRequest",
    "ImageRequest",
    "AddColorRequest",
    "UpscaleImageRequest",
)

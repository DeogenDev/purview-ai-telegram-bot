"""Хендлеры бота"""

from .start import router as start_router
from .generate_video import router as generate_video_router
from .processing_image import router as processing_image_router
from .remove_background import router as remove_background_router
from .add_color import router as add_color_router

__all__ = (
    "start_router",
    "generate_video_router",
    "processing_image_router",
    "remove_background_router",
    "add_color_router",
)

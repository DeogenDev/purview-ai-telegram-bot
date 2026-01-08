"""Хендлеры бота"""

from .start import router as start_router
from .generate import router as generate_router
from .choise import router as choise_router

__all__ = ("start_router", "generate_router", "choise_router")

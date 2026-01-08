"""Утилиты."""

from src.shared import bot, conf
from .notify import ErrorNotify, GenerationNotify
from .exctract_image import extract_image_from_message


error_notify = ErrorNotify(conf.bot.admin_id, bot)
generation_notify = GenerationNotify(conf.bot.admin_id, bot)

__all__ = ("error_notify", "generation_notify", "extract_image_from_message")

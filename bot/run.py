"""Запуск телеграм-бота"""

import logging

from aiogram import Bot, Dispatcher
from app.shared.config import conf
from .handlers import (
    start_router,
    generate_video_router,
    processing_image_router,
    remove_background_router,
    add_color_router,
)
from .middleware import AlbumMiddleware, AuthMiddleware

logger = logging.getLogger(__name__)

bot = Bot(token=conf.bot.token)
dp = Dispatcher()


async def run_bot():
    logger.info("Starting bot")
    dp.include_routers(
        start_router,
        generate_video_router,
        processing_image_router,
        remove_background_router,
        add_color_router,
    )
    dp.message.middleware(AlbumMiddleware())
    dp.message.middleware(AuthMiddleware())
    await dp.start_polling(bot)

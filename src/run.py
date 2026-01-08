"""Запуск бота."""

from aiogram import Dispatcher

from .app.handlers import start_router, generate_router, choise_router
from .app.middlewares import AuthMiddleware, AlbumMiddleware

from .shared.bot import bot


async def main():
    dp = Dispatcher()
    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(AlbumMiddleware())
    dp.include_routers(start_router, generate_router, choise_router)

    await dp.start_polling(bot)

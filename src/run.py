"""Запуск бота."""

from shared.bot import bot
from aiogram import Dispatcher

from app.middlewares import AuthMiddleware, AlbumMiddleware


async def main():
    dp = Dispatcher()
    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(AlbumMiddleware())

    await dp.start_polling(bot)

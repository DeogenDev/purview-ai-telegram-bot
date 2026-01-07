"""Инициализация бота."""

from aiogram import Bot

from shared.config import conf

bot = Bot(token=conf.bot.token)

"""Инициализация бота."""

from aiogram import Bot

from src.shared.config import conf

bot = Bot(token=conf.bot.token)

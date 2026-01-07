"""Уведомление админа"""

from aiogram import Bot
from aiogram.types import Message

from app.shared.config import conf


def create_admin_notify(message: Message, text: str):
    """СОздание сообщения для админа"""
    return f"💥 Пользователь @{message.from_user.username}\n\n{text}"


async def notify_admin(bot: Bot, message: Message, text: str):
    notify_text = create_admin_notify(message, text)
    await bot.send_message(chat_id=conf.bot.admin_id, text=notify_text)

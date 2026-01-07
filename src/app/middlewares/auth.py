"""Мидлвар доступа к боту."""

from typing import Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from shared import conf


class AuthMiddleware(BaseMiddleware):
    NOT_ACCESS_TEXT = "⛔ У вас нет доступа. Свяжитесь с администратором. @DeogenDev"

    def __init__(self) -> None:
        self.managers = set(conf.bot.managers)
        self.admin_id = conf.bot.admin_id

    async def __call__(
        self,
        handler,
        event: Union[Message, CallbackQuery],
        data: dict,
    ) -> None:
        user_id = event.from_user.id

        if user_id == self.admin_id or user_id in self.managers:
            return await handler(event, data)

        return None

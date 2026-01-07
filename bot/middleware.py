import asyncio
from collections import defaultdict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Union

from app.shared import conf


class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: float = 0.4):
        self.latency = latency
        self._albums: dict[str, list[Message]] = defaultdict(list)

    async def __call__(self, handler, event: Message, data: dict):
        if not event.media_group_id:
            return await handler(event, data)

        album_id = event.media_group_id
        self._albums[album_id].append(event)

        if len(self._albums[album_id]) > 1:
            return

        async def release():
            await asyncio.sleep(self.latency)
            messages = tuple(self._albums.pop(album_id, []))
            if messages:
                data["messages"] = messages
                await handler(event, data)

        asyncio.create_task(release())


class AuthMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.managers = set(conf.bot.managers)
        self.admin_id = conf.bot.admin_id

    async def __call__(
        self,
        handler,
        event: Union[Message, CallbackQuery],
        data: dict,
    ):
        user_id = event.from_user.id

        if user_id == self.admin_id or user_id in self.managers:
            return await handler(event, data)

        if isinstance(event, Message):
            await event.answer(
                "⛔ У вас нет доступа. Свяжитесь с администратором. @DeogenDev"
            )
            return None

        if isinstance(event, CallbackQuery):
            await event.answer(
                "⛔ У вас нет доступа. Свяжитесь с администратором. @DeogenDev",
                show_alert=True,
            )
            return None

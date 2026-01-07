"""Мидлвар обработки альбомов."""

import asyncio
from collections import defaultdict
from aiogram import BaseMiddleware
from aiogram.types import Message


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

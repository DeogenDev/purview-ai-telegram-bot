"""Уведомление админа"""

from abc import ABC

from aiogram import Bot


class NotifyBase(ABC):
    PREFIX_TEXT: str

    def __init__(self, admin_id: int, bot: Bot):
        self.admin_id = admin_id
        self.bot = bot

    async def send_admin(self, user_name: str, text: str):
        await self.bot.send_message(
            chat_id=self.admin_id,
            text=self._notify_text(user_name, text),
        )

    def _notify_text(self, user_name: str, text: str) -> str:
        return self.PREFIX_TEXT.format(user_name=user_name, text=text)


class ErrorNotify(NotifyBase):
    PREFIX_TEXT = "🆘 Ошибка. Пользователь - @{user_name}, текст ошибки - \n\n{text}"


class GenerationNotify(NotifyBase):
    PREFIX_TEXT = "⚙️ Генерация. Пользователь @{user_name} выполнил генерацию. - \n\n{text}"

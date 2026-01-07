"""Клавиатура для стартового сообщения"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .callback_data import ChoiceCallbackData


start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Создать видео", callback_data=ChoiceCallbackData.generate_video
            ),
            InlineKeyboardButton(
                text="Обработать изображение",
                callback_data=ChoiceCallbackData.processing_image,
            ),
        ],
        [
            InlineKeyboardButton(
                text="Убрать фон", callback_data=ChoiceCallbackData.remove_background
            ),
            InlineKeyboardButton(
                text="Добавить цвет", callback_data=ChoiceCallbackData.add_color
            ),
        ],
    ]
)

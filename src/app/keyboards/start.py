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
        [
            InlineKeyboardButton(
                text="Улучшить качество", callback_data=ChoiceCallbackData.upscale_image
            )
        ],
    ]
)


cancel_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]]
)

new_generation = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Новая генерация", callback_data="start_new_generation"
            )
        ]
    ]
)

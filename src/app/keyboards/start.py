"""Клавиатура для стартового сообщения"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .callback_data import ChoiceCallbackData


start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Обработать изображение",
                callback_data=ChoiceCallbackData.processing_image,
            ),
        ],
        [
            InlineKeyboardButton(
                text="Сделать фото на документы",
                callback_data=ChoiceCallbackData.create_docs_photo,
            ),
        ]
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

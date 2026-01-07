"""Клавиатуры для бота"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Создать видео", callback_data="generate_video"),
            InlineKeyboardButton(
                text="Обработать изображение", callback_data="process_image"
            ),
        ],
        [
            InlineKeyboardButton(text="Убрать фон", callback_data="remove_background"),
            InlineKeyboardButton(text="Добавить цвет", callback_data="add_color"),
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

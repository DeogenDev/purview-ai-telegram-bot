"""Хендлер старта для бота"""

from aiogram import Router, types, F
from aiogram.filters import Command
from ..keyboards import start_keyboard

from aiogram.fsm.context import FSMContext


router = Router()

START_TEXT = (
    "👋 Привет!\n\n"
    "Я бот для работы с медиа 📸🎬\n"
    "Выбери, что хочешь сделать:\n\n"
    "❔ Связаться с администратором: @DeogenDev"
)


@router.message(Command("start"))
async def start_message(message: types.Message, state=FSMContext):
    await message.answer(
        START_TEXT,
        reply_markup=start_keyboard,
    )
    await state.clear()


@router.callback_query(F.data.in_({"start_new_generation", "cancel"}))
async def start_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete_reply_markup()
    await callback.message.answer(
        START_TEXT,
        reply_markup=start_keyboard,
    )

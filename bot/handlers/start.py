"""Хендлер старта для бота"""

from aiogram import Router, types, F
from aiogram.filters import Command
from ..keyboards import start_keyboard

from aiogram.fsm.context import FSMContext


router = Router()

start_text = (
    "👋 Привет!\n\n"
    "Я бот для работы с медиа 📸🎬\n"
    "Выбери, что хочешь сделать:\n\n"
    "❔ Связаться с администратором: @DeogenDev"
)


@router.message(Command("start"))
async def start(message: types.Message, state=FSMContext):
    await message.answer(
        start_text,
        reply_markup=start_keyboard,
    )
    await state.clear()


@router.callback_query(F.data == "start_new_generation")
async def start_new_generation(callback: types.CallbackQuery, state=FSMContext):
    await callback.message.answer(
        start_text,
        reply_markup=start_keyboard,
    )
    await state.clear()


@router.callback_query(F.data == "cancel")
async def cancel(callback: types.CallbackQuery, state=FSMContext):
    await callback.message.edit_text(
        start_text,
        reply_markup=start_keyboard,
    )
    await state.clear()

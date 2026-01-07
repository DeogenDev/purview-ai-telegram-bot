"""Хендлер удаления фона"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from ..state import GenerateState

from app.services import replicate_service, RemoveBackgroundRequest
from aiogram.fsm.context import FSMContext

from ..keyboards import cancel_keyboard, new_generation
from ..services.extract_image import extract_image_from_message
from ..services.notify_admin import notify_admin

router = Router()

remove_bg_text = (
    "📷 Выбрана функция: *Удаление фона*\n\n"
    "🖼 Пожалуйста, отправьте изображение для обработки.\n\n"
    "ℹ️ Поддерживаются форматы:\n"
    "• Без сжатия (рекомендуется для лучшего качества)\n"
    "• С сжатием (допустимо, но качество ниже)\n\n"
    "✨ Для наилучшего результата используйте изображения без сжатия."
)


generate_text = (
    "⚙️ Начинается процесс генерации...\n"
    "⏳ Пожалуйста, подождите — это может занять немного времени."
)


@router.callback_query(F.data == "remove_background")
async def remove_background_callback(callback: CallbackQuery, state=FSMContext):
    await state.set_state(GenerateState.REMOVE_BACKGROUND)
    print(await state.get_state())
    await callback.message.edit_text(
        text=remove_bg_text,
        reply_markup=cancel_keyboard,
    )


@router.message((F.document | F.photo), GenerateState.REMOVE_BACKGROUND)
async def remove_background(message: Message, state: FSMContext):
    try:
        await state.clear()
        image = await extract_image_from_message(message)
        if not image:
            await message.answer(
                "🟠 Нужно отправить изображение. Начните заново!",
                reply_markup=cancel_keyboard,
            )
            return
        await message.answer(generate_text)

        output = await replicate_service.generate(RemoveBackgroundRequest(image=image))
        await message.answer_document(output.url, reply_markup=new_generation)
        await notify_admin(message.bot, message, "Удаление фона.")
    except Exception as e:
        await message.answer(
            "❌ Произошла ошибка, уведомление отправлено администратору."
        )
        await notify_admin(
            message.bot, message, f"Произошла ошибка, при удалении фона - \n\n {e}"
        )

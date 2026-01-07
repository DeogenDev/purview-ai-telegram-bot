"""Хендлер для добавления цвета"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from ..state import GenerateState

from app.services import replicate_service, AddColorRequest
from aiogram.fsm.context import FSMContext

from ..keyboards import cancel_keyboard, new_generation
from ..services.extract_image import extract_image_from_message
from ..services.notify_admin import notify_admin

router = Router()

color_text = (
    "📷 Выбрана функция: *Добавление цвета*\n\n"
    "🖼 Отправьте изображение для обработки.\n\n"
    "ℹ️ Поддерживаются форматы:\n"
    "• Без сжатия (рекомендуется для высокого качества)\n"
    "• С сжатием (допустимо, но качество ниже)\n\n"
    "✨ Для наилучшего результата используйте изображения без сжатия."
)


@router.callback_query(F.data == "add_color")
async def add_color_callback(callback: CallbackQuery, state=FSMContext):
    await state.set_state(GenerateState.ADD_COLOR)
    print(await state.get_state())
    await callback.message.edit_text(
        text=color_text,
        reply_markup=cancel_keyboard,
    )


@router.message((F.document | F.photo), GenerateState.ADD_COLOR)
async def add_color(message: Message, state: FSMContext):
    try:
        await state.clear()
        image = await extract_image_from_message(message)
        if not image:
            await message.answer("🟠 Нужно отправить изображение. Начните заново!")
            return
        await message.answer("Добавление цвета...")

        output = await replicate_service.generate(AddColorRequest(image=image))
        await message.answer_document(output.url, reply_markup=new_generation)
        await notify_admin(message.bot, message, "Добавление цвета.")
    except Exception as e:
        await message.answer(
            "❌ Произошла ошибка, уведомление отправлено администратору."
        )
        await notify_admin(
            message.bot, message, f"Произошла ошибка, при генерации видео - \n\n {e}"
        )

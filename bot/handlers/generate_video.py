"""Генерация видео"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from ..state import GenerateState

from aiogram.fsm.context import FSMContext

from ..keyboards import cancel_keyboard, new_generation
from ..services.extract_image import extract_image_from_message
from ..services.notify_admin import notify_admin

from app.services import replicate_service, VideoRequest

router = Router()

generate_video_text = (
    "🎞 Выбрана функция: *Генерация видео из изображения*\n\n"
    "🖼 Напишите описание того, что должно происходить в видео.\n\n"
    "✨ Например:\n"
    "• Камера плавно приближается к объекту\n"
    "• Изображение оживает и начинает двигаться\n"
    "• Добавляются эффекты света или цвета\n"
    "• Появляется текст или анимация\n\n"
)

save_description_text = (
    "✅ Описание сохранено!\n\n"
    "📂 Теперь отправьте изображение *как файл*.\n\n"
    "ℹ️ Это позволит сохранить качество."
)


@router.callback_query(F.data == "generate_video")
async def generate_video_callback(callback: CallbackQuery, state=FSMContext):
    await state.set_state(GenerateState.GENERATE_VIDEO)
    print(await state.get_state())
    await callback.message.edit_text(
        text=generate_video_text,
        reply_markup=cancel_keyboard,
    )


@router.message(F.text, GenerateState.GENERATE_VIDEO)
async def handle_caption(message: Message, state: FSMContext):
    await state.update_data(caption=message.text)

    await message.answer(
        save_description_text,
        parse_mode="Markdown",
    )


@router.message(
    (F.document | F.photo),
    GenerateState.GENERATE_VIDEO,
)
async def handle_images(
    message: Message,
    state: FSMContext,
):
    try:
        image = await extract_image_from_message(message)
        data = await state.get_data()
        caption: str | None = data.get("caption")

        if not image:
            await message.answer("🟠 Нужно отправить изображение. Начните заново!")
            return

        await message.answer("Генерация видео...")

        output = await replicate_service.generate(
            VideoRequest(start_image=image, prompt=caption)
        )
        await state.clear()
        await message.answer_document(output.url, reply_markup=new_generation)
        await notify_admin(message.bot, message, "Генерация видео")
    except Exception as e:
        await message.answer(
            "❌ Произошла ошибка, уведомление отправлено администратору."
        )
        await notify_admin(
            message.bot, message, f"Произошла ошибка, при генерации видео - \n\n {e}"
        )

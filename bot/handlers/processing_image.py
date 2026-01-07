"""Обработка фото"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from ..state import GenerateState

from app.services import replicate_service, ImageRequest
from aiogram.fsm.context import FSMContext
from ..services.extract_image import extract_image_from_message

from ..services.notify_admin import notify_admin
from ..keyboards import cancel_keyboard, new_generation

router = Router()

process_photo_text = (
    "📷 Выбрана функция: *Обработка фото*\n\n"
    "🖼 Напишите описание того, что нужно сделать с изображением/ями.\n\n"
    "✨ Например:\n"
    "• Сделай другую прическу\n"
    "• Обьедени фотографии в одно селфи (Если фото несколько)\n\n"
)

save_description_text = (
    "✅ Описание сохранено!\n\n"
    "📂 Теперь отправьте изображения *как файлы* (альбомом).\n\n"
    "ℹ️ Это позволит сохранить качество и корректно обработать все фото."
    "\n\n🧩 Есть возможность отправить несколько изображений в одно."
)

generation_start_text = (
    "✅ Изображения и описание получены!\n\n"
    "⚙️ Начинается процесс генерации...\n"
    "⏳ Пожалуйста, подождите — это может занять немного времени."
)


@router.callback_query(F.data == "process_image")
async def process_image_callback(callback: CallbackQuery, state=FSMContext):
    await state.set_state(GenerateState.PROCESS_IMAGE)
    print(await state.get_state())
    await callback.message.edit_text(
        text=process_photo_text,
        reply_markup=cancel_keyboard,
    )


@router.message(F.text, GenerateState.PROCESS_IMAGE)
async def handle_caption(message: Message, state: FSMContext):
    await state.update_data(caption=message.text)

    await message.answer(
        save_description_text,
        parse_mode="Markdown",
    )


@router.message(
    (F.document | F.photo) | F.media_group_id,
    GenerateState.PROCESS_IMAGE,
)
async def handle_images(
    message: Message,
    state: FSMContext,
    messages: tuple[Message, ...] | None = None,  # album
):
    try:
        data = await state.get_data()
        caption: str | None = data.get("caption")

        if not caption:
            await message.answer("Сначала отправьте описание текстом.")
            return

        image_inputs: list[str] = []

        # ---- Если это альбом ----
        if messages:  # пришли несколько сообщений
            msgs = sorted(messages, key=lambda m: m.message_id)
        else:
            msgs = [message]  # одиночный документ/фото

        for msg in msgs:
            # Проверяем только картинки
            if (
                not (msg.document and msg.document.mime_type.startswith("image/"))
                and not msg.photo
            ):
                continue

            img = await extract_image_from_message(msg)
            if img:
                image_inputs.append(img)

        if not image_inputs:
            await message.answer("Не найдено изображений.")
            return

        await state.clear()
        await message.answer(
            generation_start_text,
        )

        output = await replicate_service.generate(
            ImageRequest(
                prompt=caption,
                image_input=image_inputs,
            )
        )

        await message.answer_document(output.url, reply_markup=new_generation)
        await notify_admin(message.bot, message, "Обработка фото")

    except Exception as e:
        await message.answer(
            "❌ Произошла ошибка, уведомление отправлено администратору."
        )
        await notify_admin(
            message.bot, message, f"Произошла ошибка, при обработке фото - \n\n {e}"
        )

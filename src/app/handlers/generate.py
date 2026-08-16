"""Хендлеры генерации"""

import logging

import httpx

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from aiogram.types import BufferedInputFile


from ..states import GenerateState
from src.services import (
    toapis_service,
    ImageRequest,
    CreateDocsPhotoRequest,
)
from src.app.texts import (
    ProcessingImage,
    CreateDocsPhoto,
)
from src.app.keyboards import cancel_keyboard, new_generation
from src.app.utils import extract_image_from_message, error_notify, generation_notify

logger = logging.getLogger(__name__)
router = Router()

generate_map_state = {
    GenerateState.PROCESS_IMAGE: ImageRequest,
    GenerateState.CREATE_DOCS_PHOTO: CreateDocsPhotoRequest,
}

description_map_state = {
    GenerateState.PROCESS_IMAGE: ProcessingImage.SAVE_DESCRIPTION_TEXT,
}

generation_map_state = {
    GenerateState.PROCESS_IMAGE: ProcessingImage.GENERATION_TEXT,
    GenerateState.CREATE_DOCS_PHOTO: CreateDocsPhoto.GENERATION_TEXT,
}


@router.message(
    (F.document | F.photo),
    StateFilter(
        GenerateState.CREATE_DOCS_PHOTO
    ),
)
async def generate_wihout_description(message: Message, state: FSMContext):
    """Хендлер для генерации изображения без описания."""
    try:
        current_state = await state.get_state()
        logger.info("Getting photo: %s", current_state)
        if current_state not in generate_map_state:
            await message.answer(
                "🟠 Неизвестное состояние. Попробуйте начать заново.",
                reply_markup=cancel_keyboard,
            )
            return

        image_base_64 = await extract_image_from_message(message)
        if not image_base_64:
            await message.answer(
                "🟠 Нужно отправить изображение. Начните заново!",
                reply_markup=cancel_keyboard,
            )
            return
        await message.answer(generation_map_state[current_state], parse_mode="Markdown")

        request_class = generate_map_state[current_state]
        request = request_class(image=image_base_64)

        output_url = await toapis_service.generate(request)
        async with httpx.AsyncClient() as client:
            resp = await client.get(output_url)
            if resp.status_code == 200:
                file_bytes = resp.content
                if len(file_bytes) <= 52428800: 
                    photo = BufferedInputFile(file_bytes, filename="upscaled.png")
                    await message.answer_document(photo, reply_markup=new_generation)
                else:
                    await message.answer(f"💾 Файл слишком тяжелый (>50MB). Вот ссылка: {output_url}")
        await state.clear()
        logger.info("Generated image %s", output_url)
        await generation_notify.send_admin(
            message.from_user.username,
            f"Обработка фото — {current_state.split('.')[-1]}",
        )

    except Exception as e:
        logger.error(e)
        await state.clear()
        await error_notify.send_admin(message.from_user.username, e)
        await message.answer(
            "❌ Произошла ошибка, уведомление отправлено администратору."
        )


@router.message(
    F.text, StateFilter(GenerateState.PROCESS_IMAGE)
)
async def save_description(message: Message, state: FSMContext):
    logger.info("Saving description: %s", message.text)
    current_state = await state.get_state()
    save_description_text = description_map_state[current_state]
    await state.update_data(caption=message.text)
    await message.answer(
        save_description_text,
        parse_mode="Markdown",
    )


@router.message(
    (F.document | F.photo) | F.media_group_id,
    GenerateState.PROCESS_IMAGE,
)
async def processing_image(
    message: Message,
    state: FSMContext,
    messages: tuple[Message, ...] | None = None,  # album
):
    try:
        data = await state.get_data()
        caption: str | None = data.get("caption")

        if caption is None:
            await message.answer("Отсутствует описание, начните заново.")
            return

        images: list[str] = []

        if messages:  # multiple messages (album)
            msgs = sorted(messages, key=lambda m: m.message_id)
        else:
            msgs = [message]  # single document/photo

        for msg in msgs:
            image = await extract_image_from_message(msg)
            if image:
                images.append(image)

        if not images:
            await message.answer("Изображения не найдены, начните заново.")
            return

        await state.clear()
        await message.answer(ProcessingImage.GENERATION_TEXT)

        output = await toapis_service.generate(
            ImageRequest(
                prompt=caption,
                image_input=images,
            )
        )

        await message.answer_document(output, reply_markup=new_generation)
        await generation_notify.send_admin(
            message.from_user.username,
            "Обработка фото.",
        )

    except Exception as e:
        await message.answer(
            "❌ Произошла ошибка, уведомление отправлено администратору."
        )
        await error_notify.send_admin(
            message.from_user.username,
            f"Ошибка при обработке фото - {e}",
        )

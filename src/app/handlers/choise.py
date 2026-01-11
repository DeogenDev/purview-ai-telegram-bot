"""Хендлер выбора генерации."""

import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from ..states import GenerateState
from ..keyboards import ChoiceCallbackData, cancel_keyboard
from ..texts import (
    ProcessingImage,
    GenerateVideo,
    RemoveBackground,
    AddColor,
    UpscaleImage,
)

logger = logging.getLogger(__name__)
router = Router()

choise_map_state = {
    ChoiceCallbackData.processing_image: GenerateState.PROCESS_IMAGE,
    ChoiceCallbackData.generate_video: GenerateState.GENERATE_VIDEO,
    ChoiceCallbackData.remove_background: GenerateState.REMOVE_BACKGROUND,
    ChoiceCallbackData.add_color: GenerateState.ADD_COLOR,
    ChoiceCallbackData.upscale_image: GenerateState.UPSCALE_IMAGE,
}

choise_map_texts = {
    ChoiceCallbackData.processing_image: ProcessingImage.ABOUT_TEXT,
    ChoiceCallbackData.generate_video: GenerateVideo.ABOUT_TEXT,
    ChoiceCallbackData.remove_background: RemoveBackground.ABOUT_TEXT,
    ChoiceCallbackData.add_color: AddColor.ABOUT_TEXT,
    ChoiceCallbackData.upscale_image: UpscaleImage.ABOUT_TEXT,
}


@router.callback_query(F.data.in_(ChoiceCallbackData.choice()))
async def choise_generation(callback: CallbackQuery, state: FSMContext):
    await state.set_state(choise_map_state[callback.data])
    logger.info("Choisen generation: %s", await state.get_state())
    await callback.message.edit_text(
        text=choise_map_texts[callback.data],
        reply_markup=cancel_keyboard,
        parse_mode="Markdown",
    )

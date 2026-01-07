"""Хендлер выбора генерации."""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from ..states import GenerateState
from ..keyboards import ChoiceCallbackData
from ..texts import ProcessingImage, GenerateVideo, RemoveBackground, AddColor


choise_map_state = {
    ChoiceCallbackData.processing_image: GenerateState.PROCESS_IMAGE,
    ChoiceCallbackData.generate_video: GenerateState.GENERATE_VIDEO,
    ChoiceCallbackData.remove_background: GenerateState.REMOVE_BACKGROUND,
    ChoiceCallbackData.add_color: GenerateState.ADD_COLOR,
}

choise_map_texts = {
    ChoiceCallbackData.processing_image: ProcessingImage.ABOUT_TEXT,
    ChoiceCallbackData.generate_video: GenerateVideo.ABOUT_TEXT,
    ChoiceCallbackData.remove_background: RemoveBackground.ABOUT_TEXT,
    ChoiceCallbackData.add_color: AddColor.ABOUT_TEXT,
}

router = Router()


@router.callback_query(F.data.in_(ChoiceCallbackData.choices()))
async def choise_generation(callback: CallbackQuery, state: FSMContext):
    await state.set_state(choise_map_state[callback.data])
    await callback.message.edit_text(choise_map_texts[callback.data])

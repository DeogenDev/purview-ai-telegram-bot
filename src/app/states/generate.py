"""Состояния генерации."""

from aiogram.fsm.state import State, StatesGroup


class GenerateState(StatesGroup):
    """Выбор типа генерации"""

    GENERATE_VIDEO = State()
    PROCESS_IMAGE = State()
    REMOVE_BACKGROUND = State()
    ADD_COLOR = State()
    UPSCALE_IMAGE = State()

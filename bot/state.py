"""Состояния бота"""

from aiogram.fsm.state import State, StatesGroup


class GenerateState(StatesGroup):
    """Состояния бота"""

    GENERATE_VIDEO = State()
    PROCESS_IMAGE = State()
    REMOVE_BACKGROUND = State()
    ADD_COLOR = State()

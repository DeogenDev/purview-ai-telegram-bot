"""Состояния генерации."""

from aiogram.fsm.state import State, StatesGroup


class GenerateState(StatesGroup):
    """Выбор типа генерации"""

    PROCESS_IMAGE = State()
    CREATE_DOCS_PHOTO = State()

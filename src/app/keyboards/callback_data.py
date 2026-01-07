"""Схемы данных для клавиатур."""


class ChoiceCallbackData:
    processing_image = "processing_image"
    generate_video = "generate_video"
    remove_background = "remove_background"
    add_color = "add_color"

    @classmethod
    def choices(cls):
        return [f"{cls.__name__}.{choice}" for choice in cls._choices()]

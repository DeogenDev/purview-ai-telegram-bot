"""Схемы данных для клавиатур."""


class ChoiceCallbackData:
    processing_image = "processing_image"
    generate_video = "generate_video"
    remove_background = "remove_background"
    add_color = "add_color"

    @classmethod
    def choice(cls):
        return [value for key, value in cls.__dict__.items() if isinstance(value, str)]

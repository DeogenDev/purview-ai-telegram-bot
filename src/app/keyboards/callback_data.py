"""Схемы данных для клавиатур."""


class ChoiceCallbackData:
    processing_image = "processing_image"
    create_docs_photo = "create_docs_photo"

    @classmethod
    def choice(cls):
        return [value for key, value in cls.__dict__.items() if isinstance(value, str)]

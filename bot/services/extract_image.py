from aiogram.types import Message
import base64
import io


async def extract_image_from_message(msg: Message) -> str | None:
    """
    Возвращает data:<mime>;base64,<...> или None
    """
    if msg.document and msg.document.mime_type.startswith("image/"):
        file_id = msg.document.file_id
        mime = msg.document.mime_type

    elif msg.photo:
        file_id = msg.photo[-1].file_id
        mime = "image/jpeg"

    else:
        return None

    file = await msg.bot.get_file(file_id)
    buffer = io.BytesIO()
    await msg.bot.download_file(file.file_path, buffer)

    encoded = base64.b64encode(buffer.getvalue()).decode()
    return f"data:{mime};base64,{encoded}"

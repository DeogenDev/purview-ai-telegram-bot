"""Сервис ToApis — загрузка и генерация изображений.

Документация:
- https://docs.toapis.com/docs/cn/api-reference/uploads/images
- https://docs.toapis.com/docs/cn/api-reference/images/gemini-3-pro-image/generation
- https://docs.toapis.com/docs/cn/api-reference/images/gpt-image-2/edits
- https://docs.toapis.com/docs/cn/api-reference/tasks/image-status
"""

import asyncio
import base64
import logging
import random
import re
from pathlib import Path
from typing import Union

import httpx
from pydantic import BaseModel

from src.shared import conf

logger = logging.getLogger(__name__)

UPLOAD_ENDPOINT = "/v1/uploads/images"
IMAGE_GENERATION_ENDPOINT = "/v1/images/generations"

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_WAIT = 240  # секунд на ожидание задачи
POLL_INTERVAL = 5  # базовая пауза между запросами статуса

_DATA_URI_RE = re.compile(r"^data:(?P<mime>[^;,]+);base64,(?P<data>.+)$", re.S)

_MIME_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

DOCS_PHOTO_PROMPT = (
    "Micro retouching only, subtle skin clean up, remove acne and dark circles."
    "Keep original face identity 100procent unchanged, preserve original facial features. Do not change eye color, keep natural eyes exactly."
    "Straighten head and shoulders posture, change background to solid white,"
    "high-end passport photo style, extremely realistic, slight color correction, bright lighting."
)


class UploadedImage(BaseModel):
    """Результат загрузки изображения."""

    id: str
    url: str
    mime_type: str
    size: int


class ImageRequest(BaseModel):
    """Общая генерация: обработка фото по описанию."""

    model: str = conf.toapis.image_model
    prompt: str
    image_input: list[str] = []  # base64 data URI или URL
    output_format: str = "png"
    resolution: str = "1K"
    size: str = "original"
    n: int = 1


class CreateDocsPhotoRequest(BaseModel):
    """Фото на документы: подставляем фотку, генерируем по шаблону."""

    model: str = conf.toapis.image_model
    image: str  # base64 data URI или URL
    prompt: str = DOCS_PHOTO_PROMPT
    size: str = "3:4"
    output_format: str = "png"
    resolution: str = "1K"
    n: int = 1


class ToApisError(RuntimeError):
    """Ошибка сервиса ToApis."""


class ToApisService:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://toapis.com",
        image_model: str = "gemini-3-pro-image-preview",
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self.image_model = image_model

    # ---------- вспомогательное ----------

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}"}

    @staticmethod
    def _mime_by_filename(filename: str) -> str | None:
        if not filename:
            return None
        suffix = Path(filename).suffix.lower()
        for mime, ext in _MIME_EXT.items():
            if ext == suffix:
                return mime
        return None

    def _raise_api_error(self, resp: httpx.Response, body: dict) -> None:
        if resp.is_success and body.get("success") is not False:
            return
        error = body.get("error") or {}
        message = (
            body.get("message")
            or error.get("message")
            or error.get("code")
            or body.get("fail_reason")
            or body
        )
        raise ToApisError(f"HTTP {resp.status_code}: {message}")

    async def check_balance(self) -> dict:
        """Проверка баланса текущего API-ключа."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self._base_url}/v1/balance",
                headers=self._headers(),
            )
        body = resp.json()
        self._raise_api_error(resp, body)
        return body

    @staticmethod
    def _is_data_uri(value: str) -> bool:
        return value.startswith("data:")

    def _decode_data_uri(self, value: str) -> tuple[str, bytes]:
        match = _DATA_URI_RE.match(value)
        if not match:
            raise ToApisError("Некорректный base64 data URI")
        return match.group("mime"), base64.b64decode(match.group("data"))

    async def _resolve_image_url(self, image: str) -> str:
        """Принимает URL или base64 data URI, возвращает публичный URL."""
        if self._is_data_uri(image):
            mime, content = self._decode_data_uri(image)
            filename = f"image{_MIME_EXT.get(mime, '.png')}"
            uploaded = await self.upload_bytes(content, filename, mime_type=mime)
            return uploaded.url
        return image

    async def _resolve_image_urls(self, images: list[str]) -> list[str]:
        return [await self._resolve_image_url(img) for img in images]

    # ---------- загрузка ----------

    def _build_file(self, source, filename: str | None, mime_type: str | None) -> tuple:
        if isinstance(source, (str, Path)):
            path = Path(source)
            if not path.is_file():
                raise ToApisError(f"Файл не найден: {path}")
            if path.stat().st_size > MAX_FILE_SIZE:
                raise ToApisError(f"Файл слишком большой (>10MB): {path}")
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                raise ToApisError(f"Неподдерживаемый формат: {path.suffix}")
            return (
                path.name,
                path.read_bytes(),
                mime_type or self._mime_by_filename(path.name),
            )

        if isinstance(source, bytes):
            if not filename:
                raise ToApisError("filename обязателен при загрузке байтов")
            if len(source) > MAX_FILE_SIZE:
                raise ToApisError("Файл слишком большой (>10MB)")
            return (
                filename,
                source,
                mime_type or self._mime_by_filename(filename),
            )

        if isinstance(source, tuple) and len(source) == 2:
            name, content = source
            if len(content) > MAX_FILE_SIZE:
                raise ToApisError("Файл слишком большой (>10MB)")
            return (
                str(name),
                content,
                mime_type or self._mime_by_filename(str(name)),
            )

        raise ToApisError(
            "source должен быть str/Path, bytes или кортежем (filename, content)"
        )

    async def upload(
        self,
        source,
        *,
        purpose: str = "generation",
        filename: str | None = None,
        mime_type: str | None = None,
    ) -> UploadedImage:
        """Загрузка изображения.

        source: путь (str/Path), байты или кортеж (filename, content).
        """
        file = self._build_file(source, filename, mime_type)
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self._base_url}{UPLOAD_ENDPOINT}",
                headers=self._headers(),
                files={"file": file},
                data={"purpose": purpose},
            )
        body = resp.json()
        self._raise_api_error(resp, body)
        data = body.get("data") or {}
        return UploadedImage(
            id=data.get("id"),
            url=data["url"],
            mime_type=data.get("mime_type"),
            size=data.get("size"),
        )

    async def upload_file(
        self, file_path: str | Path, *, purpose: str = "generation"
    ) -> UploadedImage:
        """Загрузка изображения из файла."""
        return await self.upload(file_path, purpose=purpose)

    async def upload_bytes(
        self,
        content: bytes,
        filename: str,
        *,
        purpose: str = "generation",
        mime_type: str | None = None,
    ) -> UploadedImage:
        """Загрузка изображения из байтов."""
        return await self.upload(
            content, purpose=purpose, filename=filename, mime_type=mime_type
        )

    async def upload_image_url(
        self,
        source,
        *,
        purpose: str = "generation",
        filename: str | None = None,
        mime_type: str | None = None,
    ) -> str:
        """Удобный вариант: возвращает сразу URL загруженной картинки."""
        result = await self.upload(
            source, purpose=purpose, filename=filename, mime_type=mime_type
        )
        return result.url

    # ---------- генерация ----------

    async def _create_image_task(self, payload: dict) -> str:
        payload.setdefault("n", 1)
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self._base_url}{IMAGE_GENERATION_ENDPOINT}",
                headers={**self._headers(), "Content-Type": "application/json"},
                json=payload,
            )
        body = resp.json()
        self._raise_api_error(resp, body)
        task_id = body.get("id")
        if not task_id:
            raise ToApisError(f"Ответ генерации без id: {body}")
        return task_id

    async def _wait_task(self, endpoint: str, task_id: str) -> str:
        """Поллинг статуса задачи, возвращает URL результата."""
        start = asyncio.get_event_loop().time()
        interval = POLL_INTERVAL
        async with httpx.AsyncClient(timeout=120) as client:
            while asyncio.get_event_loop().time() - start < MAX_WAIT:
                resp = await client.get(
                    f"{self._base_url}{endpoint}/{task_id}",
                    headers=self._headers(),
                )
                if resp.status_code == 429:
                    await asyncio.sleep(interval + random.uniform(0, 1))
                    interval = min(interval * 2, 60)
                    continue
                body = resp.json()
                self._raise_api_error(resp, body)

                status = body.get("status")
                if status == "completed":
                    url = self._result_url(body)
                    if url:
                        return url
                    raise ToApisError(f"completed без URL: {body}")
                if status == "failed":
                    error = body.get("error") or {}
                    raise ToApisError(
                        f"Генерация не удалась: {error.get('message') or body}"
                    )

                logger.info("Task %s status=%s", task_id, status)
                await asyncio.sleep(interval + random.uniform(0, 1))

        raise ToApisError(f"Таймаут ожидания задачи {task_id}")

    @staticmethod
    def _result_url(body: dict) -> str | None:
        result = body.get("result") or {}
        data = result.get("data") or []
        for item in data:
            url = item.get("url")
            if url:
                return url
        return None

    async def _generate_image_payload(self, prompt: str, urls: list[str]) -> str:
        """Общая генерация: промпт + список референсных картинок."""
        payload: dict = {
            "model": self.image_model,
            "prompt": prompt,
            "n": 1,
            "output_format": "png",
        }
        if urls:
            payload["image_urls"] = urls
        task_id = await self._create_image_task(payload)
        return await self._wait_task(IMAGE_GENERATION_ENDPOINT, task_id)

    async def generate_image(self, request: ImageRequest) -> str:
        """Обработка фото: генерирует изображение по описанию, возвращает URL."""
        urls = await self._resolve_image_urls(request.image_input)
        return await self._generate_image_payload(request.prompt, urls)

    async def create_docs_photo(self, request: CreateDocsPhotoRequest) -> str:
        """Фото на документы по шаблону: подставляем фотку, возвращает URL."""
        url = await self._resolve_image_url(request.image)
        return await self._generate_image_payload(request.prompt, [url], request.size)

    async def generate(
        self,
        request: Union[ImageRequest, CreateDocsPhotoRequest],
    ) -> str:
        """Единая точка входа."""
        if isinstance(request, ImageRequest):
            return await self.generate_image(request)
        if isinstance(request, CreateDocsPhotoRequest):
            return await self.create_docs_photo(request)
        raise ToApisError(f"Неизвестный тип запроса: {type(request)}")


toapis_service = ToApisService(
    api_key=conf.toapis.api_key,
    base_url=conf.toapis.base_url,
    image_model=conf.toapis.image_model,
)
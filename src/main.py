"""Файл запуска бота"""

import asyncio
import logging

from src.run import main

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

if __name__ == "__main__":
    logger.info("Starting bot")
    asyncio.run(main())

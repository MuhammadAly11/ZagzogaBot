import asyncio
import logging
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

from bot.handlers.quiz_handlers import router as quiz_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Bot token from environment variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set!")

# Initialize bot and dispatcher with new DefaultBotProperties
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# Register routers
dp.include_router(quiz_router)

async def main():
    logger.info("Starting bot...")
    
    # Ensure temporary directory exists
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import types, Dispatcher, Bot, filters, Router, F
from aiogram.types import ContentType

cmd_router = Router()
msg_router = Router()
@cmd_router.message(filters.CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await message.answer(f"Hello, ({message.from_user.full_name})!")

@cmd_router.message(filters.Command("help"))
async def command_help_handler(message: types.Message) -> None:
    await message.answer(f"This is zagzoga bot I can help you create PDF and telegram quizes.")

@msg_router.message(F.document.mime_type == "text/comma-separated-values")
async def csv_handler(message: types.Message) -> None:
    await message.answer(f"This is a {message.document.file_name} with type {message.document.mime_type}")

@msg_router.message(F.document)
async def document_handler(message: types.Message) -> None:
    await message.answer(f"This is a {message.document.file_name} document with type {message.document.mime_type}")

async def main() -> None:
    load_dotenv('.env')
    TOKEN = os.getenv('API_TOKEN')
    if TOKEN is None:
        logging.error("API_TOKEN is missing in the .env file!")
        exit(1)
    
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_routers(cmd_router, msg_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
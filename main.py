import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Dispatcher, Bot
from bot.handlers import commands, other, quiz

async def main() -> None:
    load_dotenv(".env")
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if TOKEN is None:
        logging.error("API_TOKEN is missing in the .env file!")
        exit(1)

    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_routers(
        commands.router,
        quiz.router,
        other.router
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

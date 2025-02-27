from aiogram import Router
from aiogram import F, types
from bot.classes.quiz_poll import QuizPoll
from bot.config.config import datafolder
import json

router = Router()


@router.message(F.document.mime_type == "application/json")
async def json_handler(message: types.Message) -> None:
    await message.answer("processing your json file ...")
    filepath = datafolder + message.document.file_name
    bot = message.bot
    await bot.download(message.document, destination=filepath)
    await message.answer("json file downloaded successfully")

    json_data = load_quiz_data(filepath)
    q_poll = QuizPoll(json_data)
    poll_list = q_poll.get_poll_parameters()
    for question in poll_list:
        await bot.send_poll(message.chat.id, **question)
    await message.answer(f"json file processed successfully: {json_data}")


def load_quiz_data(filepath: str) -> dict:
    with open(filepath, "r") as file:
        return json.load(file)

import os
import subprocess
from aiogram import Router
from aiogram import F, types
from bot.classes.quiz_poll import QuizPoll
from bot.config.config import DATA_FOLDER
import json

router = Router()


@router.message(F.document.mime_type == "application/json")
async def json_handler(message: types.Message) -> None:
    await message.answer("processing your json file ...")
    filepath = DATA_FOLDER + message.document.file_name
    bot = message.bot
    await bot.download(message.document, destination=filepath)
    await message.answer("json file downloaded successfully")

    json_data = load_quiz_data(filepath)
    q_poll = QuizPoll(json_data)
    poll_list = q_poll.get_poll_parameters()
    for question in poll_list:
        await bot.send_poll(message.chat.id, **question)
    if (create_pdf(filepath)):
        pdf_name = os.path.splitext(message.document.file_name)[0] + ".pdf"
        pdf = types.FSInputFile("template.pdf", filename=pdf_name)
        await message.answer_document(pdf, caption="here's a pdf")
        os.remove("template.pdf")


def load_quiz_data(filepath: str) -> dict:
    with open(filepath, "r") as file:
        return json.load(file)


def create_pdf(jsonpath) -> bool:
    res = subprocess.run([
        "typst",
        "compile",
        "--input",
        f"jsonpath={jsonpath}",
        "template.typ",
    ], capture_output = True, text = True)
    if res.returncode == 0:
        return True
    else:
        return False
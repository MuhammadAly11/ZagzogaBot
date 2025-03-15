# handeling rest of messages
from aiogram import Router
from aiogram import types, F

router = Router()


@router.message(F.document)
async def document_handler(message: types.Message) -> None:
    await message.answer(
        f"This is a {message.document.file_name} document with type {message.document.mime_type}"
    )

@router.message()
async def message_handler(message: types.Message) -> None:
    await message.answer(
        f"You send this message: {message.text}"
    )
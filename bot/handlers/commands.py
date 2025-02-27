from aiogram import Router
from aiogram import filters, types

router = Router()


@router.message(filters.CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await message.answer(f"Hello, ({message.from_user.full_name})!")


@router.message(filters.Command("help"))
async def command_help_handler(message: types.Message) -> None:
    await message.answer(
        "This is zagzoga bot I can help you create PDF and telegram quizes."
    )

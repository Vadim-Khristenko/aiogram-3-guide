from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

router = Router()


@router.message(StateFilter(None), Command("drinks"))
async def cmd_food(message: Message):
    await message.answer("You should write this FSM branch yourself :)")

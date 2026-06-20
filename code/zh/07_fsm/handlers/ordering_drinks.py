from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

router = Router()


@router.message(StateFilter(None), Command("drinks"))
async def cmd_food(message: Message):
    await message.answer("这个 FSM 分支需要您自己来完成 :)")

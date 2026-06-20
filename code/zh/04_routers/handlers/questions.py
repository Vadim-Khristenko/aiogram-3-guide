from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.for_questions import get_yes_no_kb

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "您对您的工作满意吗？",
        reply_markup=get_yes_no_kb()
    )


@router.message(F.text.lower() == "是")
async def answer_yes(message: Message):
    await message.answer(
        "这很好！",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(F.text.lower() == "否")
async def answer_no(message: Message):
    await message.answer(
        "遗憾...",
        reply_markup=ReplyKeyboardRemove()
    )

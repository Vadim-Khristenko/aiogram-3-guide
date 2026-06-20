from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.text)
async def message_with_text(message: Message):
    await message.answer("这是一条文本消息！")


@router.message(F.sticker)
async def message_with_sticker(message: Message):
    await message.answer("这是一个贴纸！")


@router.message(F.animation)
async def message_with_gif(message: Message):
    await message.answer("这是一个 GIF！")

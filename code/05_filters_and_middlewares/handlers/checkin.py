import asyncio

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from keyboards.checkin import get_checkin_kb
from middlewares.weekend import WeekendMessageMiddleware

router = Router()
router.message.filter(F.chat.type == "private")
router.message.middleware(WeekendMessageMiddleware())


@router.message(Command("checkin"), flags={"long_operation": "upload_video_note"})
async def cmd_checkin(message: Message):
    await asyncio.sleep(5)
    await message.answer(
        "Пожалуйста, нажмите на кнопку ниже:",
        reply_markup=get_checkin_kb()
    )


@router.callback_query(F.data == "confirm")
async def checkin_confirm(callback: CallbackQuery):
    await callback.answer(
        "Спасибо, подтверждено!",
        show_alert=True
    )

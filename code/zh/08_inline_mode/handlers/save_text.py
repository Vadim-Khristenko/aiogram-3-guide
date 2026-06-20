from typing import Optional

from aiogram import Router, F
from aiogram.filters.command import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from filters import HasLinkFilter
from states import SaveCommon, TextSave
from storage import add_link

router = Router()


@router.message(SaveCommon.waiting_for_save_start, F.text, HasLinkFilter())
async def save_text_has_link(message: Message, link: str, state: FSMContext):
    await state.update_data(link=link)
    await state.set_state(TextSave.waiting_for_title)
    await message.answer(
        text=f"好的，我在消息中找到了链接 {link}。"
             f"现在请发送标题（不超过 30 个字符）"
    )


@router.message(SaveCommon.waiting_for_save_start, F.text)
async def save_text_no_link(message: Message):
    await message.answer(
        text="嗯……我在您的消息中没有找到链接。"
             "请再试一次，或按 /cancel 取消。"
    )


@router.message(TextSave.waiting_for_title, F.text.len() <= 30)
async def title_entered_ok(message: Message, state: FSMContext):
    await state.update_data(title=message.text, description=None)
    await state.set_state(TextSave.waiting_for_description)
    await message.answer(
        text="好的，标题已收到。现在请输入描述 "
             "（同样不超过 30 个字符） "
             "或按 /skip 跳过此步骤"
    )


@router.message(TextSave.waiting_for_description, F.text.len() <= 30)
@router.message(TextSave.waiting_for_description, Command("skip"))
async def last_step(
        message: Message,
        state: FSMContext,
        command: Optional[CommandObject] = None
):
    if not command:
        await state.update_data(description=message.text)
    # 将数据保存到我们的模拟数据库
    data = await state.get_data()
    add_link(message.from_user.id, data["link"], data["title"], data["description"])
    await state.clear()
    kb = [[InlineKeyboardButton(
        text="试一试",
        switch_inline_query="links"
    )]]
    await message.answer(
        text="链接已保存！",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )


@router.message(TextSave.waiting_for_title, F.text)
@router.message(TextSave.waiting_for_description, F.text)
async def text_too_long(message: Message):
    await message.answer("标题过长。请重试")
    return

from aiogram import Router, F
from aiogram.filters.command import Command, CommandStart
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, \
    InlineKeyboardMarkup, InlineKeyboardButton

from states import SaveCommon, DeleteCommon

router = Router()


@router.message(CommandStart(magic=F.args == "add"))
@router.message(Command("save"), StateFilter(None))
async def cmd_save(message: Message, state: FSMContext):
    await message.answer(
        text="我们来保存一些内容。"
             "请发送链接或图片给我。"
             "如果您改变主意，请发送 /cancel"
    )
    await state.set_state(SaveCommon.waiting_for_save_start)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="这里是一些欢迎文字，自行完善。",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command("delete"), StateFilter(None))
async def cmd_delete(message: Message, state: FSMContext):
    kb = []
    kb.append([
        InlineKeyboardButton(
            text="选择链接",
            switch_inline_query_current_chat="links"
        )
    ])
    kb.append([
        InlineKeyboardButton(
            text="选择图片",
            switch_inline_query_current_chat="images"
        )
    ])
    await state.set_state(DeleteCommon.waiting_for_delete_start)
    await message.answer(
        text="请选择您要删除的内容：",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )


@router.message(Command(commands=["cancel"]))
async def cmd_save(message: Message, state: FSMContext):
    await message.answer("操作已取消")
    await state.clear()

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
        text="Let's save something. "
             "Send me a link or a picture. "
             "If you change your mind — send /cancel"
    )
    await state.set_state(SaveCommon.waiting_for_save_start)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Here's some startup text. Come up with your own.",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command("delete"), StateFilter(None))
async def cmd_delete(message: Message, state: FSMContext):
    kb = []
    kb.append([
        InlineKeyboardButton(
            text="Select a link",
            switch_inline_query_current_chat="links"
        )
    ])
    kb.append([
        InlineKeyboardButton(
            text="Select an image",
            switch_inline_query_current_chat="images"
        )
    ])
    await state.set_state(DeleteCommon.waiting_for_delete_start)
    await message.answer(
        text="Choose what you want to delete:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )


@router.message(Command(commands=["cancel"]))
async def cmd_save(message: Message, state: FSMContext):
    await message.answer("Action cancelled")
    await state.clear()

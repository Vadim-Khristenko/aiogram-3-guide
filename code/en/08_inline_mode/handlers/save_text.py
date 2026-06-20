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
        text=f"Okay, I found a link {link} in the message. "
             f"Now send me the title (no more than 30 characters)"
    )


@router.message(SaveCommon.waiting_for_save_start, F.text)
async def save_text_no_link(message: Message):
    await message.answer(
        text="Hmm.. I didn't find a link in your message. "
             "Try again or press /cancel to cancel."
    )


@router.message(TextSave.waiting_for_title, F.text.len() <= 30)
async def title_entered_ok(message: Message, state: FSMContext):
    await state.update_data(title=message.text, description=None)
    await state.set_state(TextSave.waiting_for_description)
    await message.answer(
        text="Okay, I see the title. Now enter a description "
             "(also no more than 30 characters) "
             "or press /skip to skip this step"
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
    # Save data to our fake database
    data = await state.get_data()
    add_link(message.from_user.id, data["link"], data["title"], data["description"])
    await state.clear()
    kb = [[InlineKeyboardButton(
        text="Try it",
        switch_inline_query="links"
    )]]
    await message.answer(
        text="Link saved!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )


@router.message(TextSave.waiting_for_title, F.text)
@router.message(TextSave.waiting_for_description, F.text)
async def text_too_long(message: Message):
    await message.answer("Title too long. Try again")
    return

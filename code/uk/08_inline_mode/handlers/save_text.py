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
        text=f"Окей, я знайшов у повідомленні посилання {link}. "
             f"Тепер відправ мені заголовок (не більше 30 символів)"
    )


@router.message(SaveCommon.waiting_for_save_start, F.text)
async def save_text_no_link(message: Message):
    await message.answer(
        text="Емм.. я не знайшов у твоєму повідомленні посилання. "
             "Спробуй ще раз або натисни /cancel, щоб скасувати."
    )


@router.message(TextSave.waiting_for_title, F.text.len() <= 30)
async def title_entered_ok(message: Message, state: FSMContext):
    await state.update_data(title=message.text, description=None)
    await state.set_state(TextSave.waiting_for_description)
    await message.answer(
        text="Так, заголовок вижу. Тепер введи опис "
             "(теж не більше 30 символів) "
             "або натисни /skip, щоб пропустити цей крок"
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
    # Зберігаємо дані в нашу ненастоящу БД
    data = await state.get_data()
    add_link(message.from_user.id, data["link"], data["title"], data["description"])
    await state.clear()
    kb = [[InlineKeyboardButton(
        text="Спробувати",
        switch_inline_query="links"
    )]]
    await message.answer(
        text="Посилання збережене!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )


@router.message(TextSave.waiting_for_title, F.text)
@router.message(TextSave.waiting_for_description, F.text)
async def text_too_long(message: Message):
    await message.answer("Занадто довгий заголовок. Спробуй ще раз")
    return

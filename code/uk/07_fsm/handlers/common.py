from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Виберіть, що хочете замовити: "
             "блюда (/food) чи напитки (/drinks).",
        reply_markup=ReplyKeyboardRemove()
    )


# Нетрудно здогадатися, що наступні два хендлери можна
# спокійно об'єднати в один, але для повноти картини залишимо так

# default_state - це те саме, що й StateFilter(None)
@router.message(StateFilter(None), Command(commands=["cancel"]))
@router.message(default_state, F.text.lower() == "скасувати")
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    # Стейт скидати не потрібно, видалимо тільки дані
    await state.set_data({})
    await message.answer(
        text="Нічого скасовувати",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "скасувати")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Дія скасована",
        reply_markup=ReplyKeyboardRemove()
    )

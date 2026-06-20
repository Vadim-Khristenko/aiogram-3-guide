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
        text="Choose what you want to order: "
             "dishes (/food) or drinks (/drinks).",
        reply_markup=ReplyKeyboardRemove()
    )


# It's easy to guess that the following two handlers can
# be easily combined into one, but we'll keep them as they are for completeness

# default_state is the same as StateFilter(None)
@router.message(StateFilter(None), Command(commands=["cancel"]))
@router.message(default_state, F.text.lower() == "cancel")
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    # No need to reset the state, just clear the data
    await state.set_data({})
    await message.answer(
        text="Nothing to cancel",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "cancel")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Action cancelled",
        reply_markup=ReplyKeyboardRemove()
    )

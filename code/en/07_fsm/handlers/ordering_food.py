from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.simple_row import make_row_keyboard

router = Router()

# These values will be substituted below in the final text, hence
# such at first glance strange form of adjectives
available_food_names = ["Sushi", "Spaghetti", "Khachapuri"]
available_food_sizes = ["Small", "Medium", "Large"]


class OrderFood(StatesGroup):
    choosing_food_name = State()
    choosing_food_size = State()


@router.message(StateFilter(None), Command("food"))
async def cmd_food(message: Message, state: FSMContext):
    await message.answer(
        text="Choose a dish:",
        reply_markup=make_row_keyboard(available_food_names)
    )
    # Set user state to "choosing name"
    await state.set_state(OrderFood.choosing_food_name)

# Food selection stage #


@router.message(OrderFood.choosing_food_name, F.text.in_(available_food_names))
async def food_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_food=message.text.lower())
    await message.answer(
        text="Thank you. Now please choose portion size:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
    await state.set_state(OrderFood.choosing_food_size)


# In general, nothing prevents you from specifying states as full strings
# This may be useful if for some reason
# your state names are generated at runtime (but why?)
@router.message(StateFilter("OrderFood:choosing_food_name"))
async def food_chosen_incorrectly(message: Message):
    await message.answer(
        text="I don't know such a dish.\n\n"
             "Please choose one of the names from the list below:",
        reply_markup=make_row_keyboard(available_food_names)
    )

# Portion size selection stage and summary information display #


@router.message(OrderFood.choosing_food_size, F.text.in_(available_food_sizes))
async def food_size_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text=f"You chose {message.text.lower()} portion of {user_data['chosen_food']}.\n"
             f"Try ordering drinks now: /drinks",
        reply_markup=ReplyKeyboardRemove()
    )
    # Resetting user state and saved data
    await state.clear()


@router.message(OrderFood.choosing_food_size)
async def food_size_chosen_incorrectly(message: Message):
    await message.answer(
        text="I don't know such size.\n\n"
             "Please choose one of the options from the list below:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )

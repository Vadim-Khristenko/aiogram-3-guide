from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.simple_row import make_row_keyboard

router = Router()

# Ці значення далі будуть підставлятися в підсумковий текст, звідси
# така на перший погляд дивна форма прикметників
available_food_names = ["Суші", "Спагеті", "Хачапурі"]
available_food_sizes = ["Маленьку", "Середню", "Велику"]


class OrderFood(StatesGroup):
    choosing_food_name = State()
    choosing_food_size = State()


@router.message(StateFilter(None), Command("food"))
async def cmd_food(message: Message, state: FSMContext):
    await message.answer(
        text="Виберіть блюдо:",
        reply_markup=make_row_keyboard(available_food_names)
    )
    # Встановлюємо користувачеві стан "вибирає назву"
    await state.set_state(OrderFood.choosing_food_name)

# Етап вибору блюда #


@router.message(OrderFood.choosing_food_name, F.text.in_(available_food_names))
async def food_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_food=message.text.lower())
    await message.answer(
        text="Дякую. Тепер, будь ласка, виберіть розмір порції:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
    await state.set_state(OrderFood.choosing_food_size)


# За все, ніхто не заважає вказувати стейти повністю рядками
# Це може знадобитися, якщо з якої-то причини
# ваші назви стейтів генеруються в рантаймі (але навіщо?)
@router.message(StateFilter("OrderFood:choosing_food_name"))
async def food_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого блюда.\n\n"
             "Будь ласка, виберіть одну з назв зі списку нижче:",
        reply_markup=make_row_keyboard(available_food_names)
    )

# Етап вибору розміру порції й відображення підсумкової інформації #


@router.message(OrderFood.choosing_food_size, F.text.in_(available_food_sizes))
async def food_size_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text=f"Ви вибрали {message.text.lower()} порцію {user_data['chosen_food']}.\n"
             f"Спробуйте тепер замовити напитки: /drinks",
        reply_markup=ReplyKeyboardRemove()
    )
    # Скидання стану й збережених даних користувача
    await state.clear()


@router.message(OrderFood.choosing_food_size)
async def food_size_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого розміру порції.\n\n"
             "Будь ласка, виберіть один з варіантів зі списку нижче:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )

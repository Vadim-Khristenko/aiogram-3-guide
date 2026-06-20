from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.simple_row import make_row_keyboard

router = Router()

# 这些值稍后将替换到最终文本中，因此
# 形容词的形式乍一看有些奇怪
available_food_names = ["寿司", "意大利面", "哈恰布里"]
available_food_sizes = ["小份", "中份", "大份"]


class OrderFood(StatesGroup):
    choosing_food_name = State()
    choosing_food_size = State()


@router.message(StateFilter(None), Command("food"))
async def cmd_food(message: Message, state: FSMContext):
    await message.answer(
        text="请选择菜肴：",
        reply_markup=make_row_keyboard(available_food_names)
    )
    # 为用户设置"选择名称"状态
    await state.set_state(OrderFood.choosing_food_name)

# 菜肴选择阶段 #


@router.message(OrderFood.choosing_food_name, F.text.in_(available_food_names))
async def food_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_food=message.text.lower())
    await message.answer(
        text="谢谢。现在请选择份量：",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
    await state.set_state(OrderFood.choosing_food_size)


# 一般来说，没有人会阻止你用完整的字符串来指定状态
# 如果出于某种原因你的状态名称在运行时生成，这可能会很有用（但为什么呢？）
@router.message(StateFilter("OrderFood:choosing_food_name"))
async def food_chosen_incorrectly(message: Message):
    await message.answer(
        text="我不知道这道菜。\n\n"
             "请从下面的列表中选择一个：",
        reply_markup=make_row_keyboard(available_food_names)
    )

# 份量选择阶段和摘要显示 #


@router.message(OrderFood.choosing_food_size, F.text.in_(available_food_sizes))
async def food_size_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text=f"您选择了 {user_data['chosen_food']} 的 {message.text.lower()} 份。\n"
             f"现在请尝试点饮料：/drinks",
        reply_markup=ReplyKeyboardRemove()
    )
    # 重置用户的状态和保存的数据
    await state.clear()


@router.message(OrderFood.choosing_food_size)
async def food_size_chosen_incorrectly(message: Message):
    await message.answer(
        text="我不知道这个份量。\n\n"
             "请从下面的列表中选择一个：",
        reply_markup=make_row_keyboard(available_food_sizes)
    )

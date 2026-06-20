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
        text="请选择您想点的：菜肴（/food）还是饮料（/drinks）。",
        reply_markup=ReplyKeyboardRemove()
    )


# 不难看出，接下来的两个处理器可以
# 轻松合并为一个，但为了完整起见，我们保留这样

# default_state - 与 StateFilter(None) 相同
@router.message(StateFilter(None), Command(commands=["cancel"]))
@router.message(default_state, F.text.lower() == "取消")
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    # 不需要重置状态，只删除数据
    await state.set_data({})
    await message.answer(
        text="没有可取消的操作",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "取消")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="操作已取消",
        reply_markup=ReplyKeyboardRemove()
    )

import asyncio
import logging
from contextlib import suppress
from random import randint
from typing import Optional

from aiogram import Bot, Dispatcher, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from config_reader import config

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

user_data = {}


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="配番茄酱"),
            types.KeyboardButton(text="不配番茄酱")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="选择配料方式"
    )
    await message.answer("炸肉饼怎么吃？", reply_markup=keyboard)


@dp.message(F.text.lower() == "配番茄酱")
async def with_puree(message: types.Message):
    await message.reply("很棒的选择！", reply_markup=types.ReplyKeyboardRemove())


@dp.message(F.text.lower() == "不配番茄酱")
async def without_puree(message: types.Message):
    await message.reply("这样不好吃！")


@dp.message(Command("reply_builder"))
async def reply_builder(message: types.Message):
    builder = ReplyKeyboardBuilder()
    for i in range(1, 17):
        builder.add(types.KeyboardButton(text=str(i)))
    builder.adjust(4)
    await message.answer(
        "选择一个数字：",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.message(Command("special_buttons"))
async def cmd_special_buttons(message: types.Message):
    builder = ReplyKeyboardBuilder()
    # row 方法允许显式地形成一行
    # 一个或多个按钮。例如，第一行
    # 将包含两个按钮...
    builder.row(
        types.KeyboardButton(text="请求地理位置", request_location=True),
        types.KeyboardButton(text="请求联系方式", request_contact=True)
    )
    # ... 第二行只有一个 ...
    builder.row(types.KeyboardButton(
        text="创建测验",
        request_poll=types.KeyboardButtonPollType(type="quiz"))
    )
    # ... 第三行再次两个
    builder.row(
        types.KeyboardButton(
            text="选择高级用户",
            request_user=types.KeyboardButtonRequestUser(
                request_id=1,
                user_is_premium=True
            )
        ),
        types.KeyboardButton(
            text="选择带有论坛的超级群组",
            request_chat=types.KeyboardButtonRequestChat(
                request_id=2,
                chat_is_channel=False,
                chat_is_forum=True
            )
        )
    )
    # WebApp 还没有，抱歉 :(

    await message.answer(
        "选择一个操作：",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.message(F.user_shared)
async def on_user_shared(message: types.Message):
    print(
        f"请求 {message.user_shared.request_id}。"
        f"用户 ID：{message.user_shared.user_id}"
    )


@dp.message(F.chat_shared)
async def on_chat_shared(message: types.Message):
    print(
        f"请求 {message.chat_shared.request_id}。"
        f"聊天 ID：{message.chat_shared.chat_id}"
    )


@dp.message(Command("inline_url"))
async def cmd_inline_url(message: types.Message, bot: Bot):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="GitHub", url="https://github.com")
    )
    builder.row(types.InlineKeyboardButton(
        text="Telegram 官方频道",
        url="tg://resolve?domain=telegram")
    )

    # 为了能够显示 ID 按钮，
    # 用户必须 False 标志 has_private_forwards
    user_id = 1234567890
    chat_info = await bot.get_chat(user_id)
    if not chat_info.has_private_forwards:
        builder.row(types.InlineKeyboardButton(
            text="某个用户",
            url=f"tg://user?id={user_id}")
        )
    await message.answer(
        '选择一个链接',
        reply_markup=builder.as_markup(),
    )


@dp.message(Command("random"))
async def cmd_random(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="点击我",
        callback_data="random_value")
    )
    await message.answer(
        "点击按钮，机器人将发送 1 到 10 之间的数字",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "random_value")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer(str(randint(1, 10)))
    await callback.answer(
        text="谢谢您使用我们的机器人！",
        show_alert=True
    )
    # 或只是 await call.answer()


# ----------
# 这是没有工厂的变体。

def get_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="-1", callback_data="num_decr"),
            types.InlineKeyboardButton(text="+1", callback_data="num_incr")
        ],
        [types.InlineKeyboardButton(text="确认", callback_data="num_finish")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def update_num_text(message: types.Message, new_value: int):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"输入数字：{new_value}",
            reply_markup=get_keyboard()
        )


@dp.message(Command("numbers"))
async def cmd_numbers(message: types.Message):
    user_data[message.from_user.id] = 0
    await message.answer("输入数字：0", reply_markup=get_keyboard())


@dp.callback_query(F.data.startswith("num_"))
async def callbacks_num(callback: types.CallbackQuery):
    user_value = user_data.get(callback.from_user.id, 0)
    action = callback.data.split("_")[1]

    if action == "incr":
        user_data[callback.from_user.id] = user_value+1
        await update_num_text(callback.message, user_value+1)
    elif action == "decr":
        user_data[callback.from_user.id] = user_value-1
        await update_num_text(callback.message, user_value-1)
    elif action == "finish":
        await callback.message.edit_text(f"总共：{user_value}")

    await callback.answer()


# ----------
# 这是带有工厂的变体

class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
    action: str
    value: Optional[int] = None


def get_keyboard_fab():
    builder = InlineKeyboardBuilder()
    builder.button(text="-2", callback_data=NumbersCallbackFactory(action="change", value=-2))
    builder.button(text="-1", callback_data=NumbersCallbackFactory(action="change", value=-1))
    builder.button(text="+1", callback_data=NumbersCallbackFactory(action="change", value=1))
    builder.button(text="+2", callback_data=NumbersCallbackFactory(action="change", value=2))
    builder.button(text="确认", callback_data=NumbersCallbackFactory(action="finish"))
    builder.adjust(4)
    return builder.as_markup()


async def update_num_text_fab(message: types.Message, new_value: int):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"输入数字：{new_value}",
            reply_markup=get_keyboard_fab()
        )


@dp.message(Command("numbers_fab"))
async def cmd_numbers_fab(message: types.Message):
    user_data[message.from_user.id] = 0
    await message.answer("输入数字：0", reply_markup=get_keyboard_fab())


# 点击其中一个按钮：-2、-1、+1、+2
@dp.callback_query(NumbersCallbackFactory.filter(F.action == "change"))
async def callbacks_num_change_fab(callback: types.CallbackQuery, callback_data: NumbersCallbackFactory):
    # 当前值
    user_value = user_data.get(callback.from_user.id, 0)

    user_data[callback.from_user.id] = user_value + callback_data.value
    await update_num_text_fab(callback.message, user_value + callback_data.value)
    await callback.answer()


# 点击"确认"按钮
@dp.callback_query(NumbersCallbackFactory.filter(F.action == "finish"))
async def callbacks_num_finish_fab(callback: types.CallbackQuery):
    # 当前值
    user_value = user_data.get(callback.from_user.id, 0)

    await callback.message.edit_text(f"总共：{user_value}")
    await callback.answer()


# 启动机器人
async def main():
    # 启动机器人并跳过所有累积的传入消息
    # 是的，即使您使用的是长轮询，也可以调用此方法
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

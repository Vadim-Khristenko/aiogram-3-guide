import asyncio
import random
from os import getenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

dp = Dispatcher()

RESPONSES = [
    "不知道。",
    "不确定。",
    "也许吧。",
    "难说。",
    "可能。",
]

@dp.guest_message(F.text)
async def any_message(
        message: Message,
):
    await message.answer_guest_query(
        result=InlineQueryResultArticle(
            id="1",
            title="任意文字，反正没人会看到",
            input_message_content=InputTextMessageContent(
                message_text=random.choice(RESPONSES),
            ),
        )
    )

async def main():
    bot_token = getenv("BOT_TOKEN")
    if not bot_token:
        error = "No token provided"
        raise ValueError(error)

    bot = Bot(token=bot_token)
    print("机器人启动中...")
    try:
        await dp.start_polling(bot)
    finally:
        print("机器人已停止")


if __name__ == '__main__':
    asyncio.run(main())

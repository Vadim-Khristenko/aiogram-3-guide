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
    "Не знаю.",
    "Не впевнений.",
    "Може бути.",
    "Важко сказати.",
    "Можливо.",
]

@dp.guest_message(F.text)
async def any_message(
        message: Message,
):
    await message.answer_guest_query(
        result=InlineQueryResultArticle(
            id="1",
            title="Будь-який текст, все одно ніхто не побачить",
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
    print("Запуск бота...")
    try:
        await dp.start_polling(bot)
    finally:
        print("Бот зупинено")


if __name__ == '__main__':
    asyncio.run(main())

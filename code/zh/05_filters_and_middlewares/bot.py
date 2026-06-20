import asyncio

from aiogram import Bot, Dispatcher

from config_reader import config
from handlers import group_games, checkin, usernames
from middlewares.slow import ChatActionMiddleware
from middlewares.weekend import WeekendCallbackMiddleware


async def main():
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    dp.include_router(group_games.router)
    dp.include_router(checkin.router)
    dp.include_router(usernames.router)

    dp.message.middleware(ChatActionMiddleware())
    dp.callback_query.outer_middleware(WeekendCallbackMiddleware())

    # 启动机器人并跳过所有累积的传入消息
    # 是的，即使您使用的是长轮询，也可以调用此方法
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

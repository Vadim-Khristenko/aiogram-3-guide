import asyncio

from aiogram import Bot, Dispatcher

from config_reader import config
from handlers import questions, different_types


# 启动机器人
async def main():
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    dp.include_routers(questions.router, different_types.router)

    # 替代方法：每行一个路由器
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)

    # 启动机器人并跳过所有累积的传入消息
    # 是的，即使您使用的是长轮询，也可以调用此方法
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

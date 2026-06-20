import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
# FSM 策略部分的额外导入
from aiogram.fsm.strategy import FSMStrategy

# 可以从存储库中获取 config_reader.py 文件
# 示例 — 在第一章中
from config_reader import config
from handlers import common, ordering_food, ordering_drinks


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # 如果不指定 storage，默认仍然会使用 MemoryStorage
    # 但明确声明更好 =]
    dp = Dispatcher(storage=MemoryStorage())
    # 选择其他 FSM 策略：
    # dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)
    bot = Bot(config.bot_token.get_secret_value())

    dp.include_routers(common.router, ordering_food.router, ordering_drinks.router)
    # 在这里导入你自己的饮料订购路由器

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

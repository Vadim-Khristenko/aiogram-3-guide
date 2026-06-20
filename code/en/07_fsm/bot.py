import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
# Additional import for FSM strategy section
from aiogram.fsm.strategy import FSMStrategy

# config_reader.py file can be taken from the repository
# example — in the first chapter
from config_reader import config
from handlers import common, ordering_food, ordering_drinks


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # If storage is not specified, MemoryStorage will be used by default anyway
    # But explicit is better than implicit =]
    dp = Dispatcher(storage=MemoryStorage())
    # To select a different FSM strategy:
    # dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)
    bot = Bot(config.bot_token.get_secret_value())

    dp.include_routers(common.router, ordering_food.router, ordering_drinks.router)
    # import your own router for drinks here

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
# Доп. імпорт для розділу про стратегії FSM
from aiogram.fsm.strategy import FSMStrategy

# файл config_reader.py можна взяти з репозиторію
# приклад — у першому розділі
from config_reader import config
from handlers import common, ordering_food, ordering_drinks


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Якщо не вказати storage, то за замовчуванням все одно буде MemoryStorage
    # Але явне краще неявного =]
    dp = Dispatcher(storage=MemoryStorage())
    # Для вибору іншої стратегії FSM:
    # dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)
    bot = Bot(config.bot_token.get_secret_value())

    dp.include_routers(common.router, ordering_food.router, ordering_drinks.router)
    # сюди імпортуйте ваш власний роутер для напитків

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

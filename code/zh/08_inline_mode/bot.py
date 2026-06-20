import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# 可以从存储库中获取 config_reader.py 文件
# 示例 — 在第一章中
from config_reader import config
from handlers import common, save_text, save_images, \
    inline_mode, delete_data, inline_pagination_demo, \
    inline_chosen_result_demo


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(config.bot_token.get_secret_value())

    dp.include_routers(
        common.router,
        save_text.router, save_images.router, delete_data.router,
        inline_mode.router, inline_pagination_demo.router,
        inline_chosen_result_demo.router
    )

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

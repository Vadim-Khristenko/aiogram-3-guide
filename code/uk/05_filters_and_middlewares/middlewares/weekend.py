from datetime import datetime
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery


def _is_weekend() -> bool:
    # 5 - субота, 6 - неділя
    return datetime.utcnow().weekday() in (5, 6)


# Це буде inner-мідлварь на повідомлення
class WeekendMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Якщо сьогодні не субота й не неділя,
        # то продовжуємо обробку.
        if not _is_weekend():
            return await handler(event, data)
        # Інакше просто повернеться None
        # і обробка припиниться


# Це буде outer-мідлварь на будь-які колбеки
class WeekendCallbackMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Якщо сьогодні не субота й не неділя,
        # то продовжуємо обробку.
        if not _is_weekend():
            return await handler(event, data)
        # Інакше відповідаємо на колбек самостійно
        # і припиняємо подальшу обробку
        await event.answer(
            "Бот у вихідні не працює!",
            show_alert=True
        )
        return

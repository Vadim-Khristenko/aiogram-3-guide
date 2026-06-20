from datetime import datetime
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery


def _is_weekend() -> bool:
    # 5 - 星期六，6 - 星期日
    return datetime.utcnow().weekday() in (5, 6)


# 这将是消息上的 inner 中间件
class WeekendMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # 如果今天不是星期六或星期日，
        # 那么我们继续处理。
        if not _is_weekend():
            return await handler(event, data)
        # 否则只会返回 None
        # 处理将停止


# 这将是任何回调上的 outer 中间件
class WeekendCallbackMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # 如果今天不是星期六或星期日，
        # 那么我们继续处理。
        if not _is_weekend():
            return await handler(event, data)
        # 否则我们自己回应回调
        # 并停止进一步处理
        await event.answer(
            "机器人在周末不工作！",
            show_alert=True
        )
        return

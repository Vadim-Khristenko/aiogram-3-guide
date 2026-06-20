from statistics import median
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender


class ChatActionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        long_operation_type = get_flag(data, "long_operation")

        # If there is no such flag on the handler
        if not long_operation_type:
            return await handler(event, data)

        # If the flag exists
        async with ChatActionSender(
                action=long_operation_type,
                chat_id=event.chat.id,
                bot=data["bot"],
        ):
            return await handler(event, data)

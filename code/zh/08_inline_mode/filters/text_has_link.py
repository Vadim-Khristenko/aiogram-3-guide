from typing import Union, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message


class HasLinkFilter(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        # 如果 entities 完全不存在，
        # 在这种情况下，视为空列表
        entities = message.entities or []

        # 如果至少有一个链接，返回它
        for entity in entities:
            if entity.type == "url":
                return {"link": entity.extract_from(message.text)}

        # 如果没有找到任何内容，返回 False
        return False

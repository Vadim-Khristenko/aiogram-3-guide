from typing import Union, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message


class HasUsernamesFilter(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        # 如果根本没有 entities，将返回 None，
        # 在这种情况下，我们认为这是一个空列表
        entities = message.entities or []

        # 检查任何用户名并使用
        # extract_from() 方法从文本中提取它们。详细信息请参见
        # 关于处理消息的章节
        found_usernames = [
            item.extract_from(message.text) for item in entities
            if item.type == "mention"
        ]

        # 如果找到了用户名，将它们"传递"给处理程序
        # 按名称"usernames"
        if len(found_usernames) > 0:
            return {"usernames": found_usernames}
        # 如果我们没有找到任何用户名，返回 False
        return False

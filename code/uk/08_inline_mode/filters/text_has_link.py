from typing import Union, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message


class HasLinkFilter(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        # Якщо entities взагалі немає, повернеться None,
        # у цьому випадку вважаємо, що це порожній список
        entities = message.entities or []

        # Якщо є хоча б одне посилання, повертаємо його
        for entity in entities:
            if entity.type == "url":
                return {"link": entity.extract_from(message.text)}

        # Якщо нічого не знайшли, повертаємо None
        return False

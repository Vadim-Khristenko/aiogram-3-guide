from typing import Union, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message


class HasUsernamesFilter(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        # Якщо entities взагалі немає, повернеться None,
        # у цьому випадку вважаємо, що це порожній список
        entities = message.entities or []

        # Перевіряємо будь-які юзернейми й витягаємо їх з тексту
        # методом extract_from(). Докладніше див. розділ
        # про роботу з повідомленнями
        found_usernames = [
            item.extract_from(message.text) for item in entities
            if item.type == "mention"
        ]

        # Якщо юзернейми є, то "проштовхуємо" їх у хендлер
        # за ім'ям "usernames"
        if len(found_usernames) > 0:
            return {"usernames": found_usernames}
        # Якщо не знайшли жодного юзернейма, повернем False
        return False

---
title: Роутери, багатофайловість і структура бота
description: Роутери, багатофайловість і структура бота
---

# Роутери, багатофайловість і структура бота

!!! info ""
    Використовувана версія aiogram: 3.7.0

У цій главі ми познайомимося з новою фішкою aiogram 3.x — роутерами, навчимося розбивати наш код на окремі 
компоненти, а також сформуємо базову структуру бота, яка стане в пригоді у наступних главах і взагалі у житті.

## Точка входу в додаток {: id="entrypoint" }

Театр починається з гардеробу, а бот починається з точки входу. Нехай це буде файл `bot.py`. У ньому ми визначимо 
асинхронну функцію `main()`, у якій створимо необхідні об'єкти та запустимо поллінг. Які 
об'єкти є необхідними? По-перше, звичайно, бот. Їх може бути кілька, але про це 
якось в іншому разі. По-друге, диспетчер. Він займається отриманням подій від Telegram та розсилкою їх 
по хендлерам через фільтри та мідлвери.

```python title="bot.py"
import asyncio
from aiogram import Bot, Dispatcher


# Запуск бота
async def main():
    bot = Bot(token="TOKEN")
    dp = Dispatcher()

    # Запускаємо бота та пропускаємо всі накопичені вхідні
    # Так, цей метод можна викликати навіть якщо у вас поллінг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

Але щоб обробляти повідомлення, цього недостатньо, потрібні ще хендлери. Ми хочемо їх розташувати 
в інших файлах, аби не створювати стіну коду на кілька тисяч рядків. У попередніх главах усі 
наші хендлери підключувалися до диспетчера, але тепер він всередині функції та ми точно не хочемо 
робити його глобальним об'єктом.  
Що ж робити? І тут на допомогу приходять...

## Роутери {: id="routers" }

Звернемося до [офіційної документації](https://docs.aiogram.dev/en/dev-3.x/dispatcher/router.html) 
aiogram 3.x та поглянемо на таке зображення: 

![Кілька роутерів](https://docs.aiogram.dev/en/dev-3.x/_images/nested_routers_example.png)

Що ми бачимо? 

1. Диспетчер — кореневий роутер.
2. Хендлери підключаються до роутерів.
3. Роутери можуть бути вкладеними, але між ними тільки однонаправлена зв'язок.
4. Порядок підключення (та, відповідно, перевірки) роутерів явно визначено.

На наступному зображенні видно порядок пошуку оновленням потрібного хендлера для виконання:

![порядок пошуку оновленням потрібного хендлера](https://docs.aiogram.dev/en/dev-3.x/_images/update_propagation_flow.png)

Напишемо простенького бота з двома фішками:

1. Якщо боту надіслали `/start`, він повинен надіслати запитання та дві кнопки з текстами «Так» і «Ні».
2. Якщо боту надіслали будь-який інший текст, стикер або гіфку, він повинен відповісти назвою типу повідомлення.

Почнемо з клавіатури: створимо поряд із файлом `bot.py` каталог `keyboards`, а всередині нього файл `for_questions.py` 
та напишемо функцію для отримання простої клавіатури з кнопками "Так" і "Ні" в один ряд:

```python title="keyboards/for_questions.py"
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_yes_no_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Так")
    kb.button(text="Ні")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
```

Нічого складного, тим більше, що ми клавіатури детально розбирали [раніше](buttons.md). 
Тепер поряд із файлом `bot.py` створимо інший каталог `handlers`, а всередину нього файл `questions.py`.

```python title="handlers/questions.py" hl_lines="7 9"
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.for_questions import get_yes_no_kb

router = Router()  # [1]

@router.message(Command("start"))  # [2]
async def cmd_start(message: Message):
    await message.answer(
        "Ви задоволені своєю роботою?",
        reply_markup=get_yes_no_kb()
    )

@router.message(F.text.lower() == "так")
async def answer_yes(message: Message):
    await message.answer(
        "Це чудово!",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text.lower() == "ні")
async def answer_no(message: Message):
    await message.answer(
        "Шкода...",
        reply_markup=ReplyKeyboardRemove()
    )
```

Зверніть увагу на пункти [1] та [2]. По-перше, ми у файлі створили свій власний роутер рівня модуля, та далі 
будемо підключувати його до кореневого роутера (диспетчера). По-друге, хендлери «відлучуються» уже від локального роутера.

Аналогічним чином зробимо другий файл із хендлерами `different_types.py`, де просто будемо виводити тип повідомлення:

```python title="handlers/different_types.py"
from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text)
async def message_with_text(message: Message):
    await message.answer("Це текстове повідомлення!")

@router.message(F.sticker)
async def message_with_sticker(message: Message):
    await message.answer("Це стикер!")

@router.message(F.animation)
async def message_with_gif(message: Message):
    await message.answer("Це GIF!")

```

Нарешті, повернемося до нашого `bot.py`, імпортуємо файли з роутерами та хендлерами, та підключимо їх до диспетчера:

```python title="bot.py" hl_lines="3 11 12"
import asyncio
from aiogram import Bot, Dispatcher
from handlers import questions, different_types


# Запуск бота
async def main():
    bot = Bot(token="TOKEN")
    dp = Dispatcher()

    dp.include_routers(questions.router, different_types.router)

    # Альтернативний варіант реєстрації роутерів по одному на рядок
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)

    # Запускаємо бота та пропускаємо всі накопичені вхідні
    # Так, цей метод можна викликати навіть якщо у вас поллінг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

Ми просто імпортуємо файли з каталогу `handlers/` та підключаємо роутери з цих файлів до диспетчера. І тут знову 
важливий порядок імпортів! Якщо ми переставимо місцями реєстрацію роутерів, то на команду `/start` бот буде відповідати 
фразою «Це текстове повідомлення!», оскільки функція `message_with_text()` першою успішно пройде всі фільтри. Але 
про самі фільтри ми поговоримо трохи пізніше, а поки що розглянемо ще одне питання.


## Підсумок {: id="conclusion" }

У нас вийшло акуратно розділити бота за різними файлами, не порушуючи його роботу. Приблизне дерево файлів 
та каталогів вийшло таким (тут свідомо пропущено деякі несуттєві для прикладу файли):

```
├── bot.py
├── handlers
│   ├── different_types.py
│   └── questions.py
├── keyboards
│   └── for_questions.py
```

Надалі ми будемо дотримуватися такої структури, плюс додадуться нові каталоги для фільтрів, мідлварів, 
файлів для роботи з базами даних тощо.

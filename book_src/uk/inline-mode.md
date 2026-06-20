---
title: Інлайн-режим
description: Інлайн-режим
---

# Інлайн-режим

!!! info ""
    Використовувана версія aiogram: 3.7.0

## Теорія {: id="theory" }

### Навіщо потрібен інлайн-режим? {: id="why-inline-mode" }

У попередніх розділах бот і людина спілкувалися один з одним, але в Telegram існує спеціальний режим, 
який дозволяє користувачеві відправити інформацію від свого імені, але за допомогою бота. Це називається **інлайн-режим** 
(Inline mode), і ось як він виглядає в реальному житті:

![Приклад роботи бота @imdb в інлайн-режимі](../images/ru/inline_mode/inline_demo.png)

Але як на практиці взагалі можна застосувати таку фічу? Пропоную подивитися на назви деяких
напіво-офіційних Telegram-ботів, які мають інлайн-режим:

* [@gif](https://t.me/gif) 
* [@wiki](https://t.me/wiki)
* [@imdb](https://t.me/imdb)
* [@youtube](https://t.me/youtube)
* [@foursquare](https://t.me/foursquare)
* [@music](https://t.me/music)
* [@gamee](https://t.me/gamee)
* [@like](https://t.me/like)

Список можна продовжувати довго, але суть, сподіваюся, зрозуміла: інлайн-режим чудово підходить для пошуку контенту для вставки 
в поточний чат. Частину можливостей таких ботів (like, poll, gif) Telegram впровадив у офіційні додатки, але решта чудово використовується і досі.

!!! warning "Важливо"
    Нагадаю, що якщо до повідомлення, відправленого з інлайн-режиму, прикріплена клавіатура з callback-кнопкою, 
    то при натисканні на неї бот отримає об'єкт `CallbackQuery` **без** об'єкта `Message` всередину. Замість 
    цього буде мало про що говорящий `inline_message_id`.

### Формат вхідних запитів {: id="incoming-update-format" }

Коли користувач пише в чаті юзернейм бота й далі вводить текст, створюється апдейт типу 
[InlineQuery](https://core.telegram.org/bots/api#inlinequery). Якщо уважно вивчити поля цього об'єкта, 
то можна помітити деякі дивності. 

По-перше, немає ID чату, з якого викликали бота, замість цього опціональне 
поле `chat_type`, яке показує (якщо непусте) **тип** чату (особистий, група, супергрупа, канал). Причина проста: 
оскільки для використання бота в інлайн-режимі не потрібно його ніде додавати, додавання об'єкта Chat 
дозволило б непомітно відслідковувати і збирати чати в телеграмі. 

По-друге, є поле `offset`, причому це не число, а рядок. Справа в тому, що за замовчуванням бот може відправити не більше 
50 результатів користувачеві у відповідь на інлайн-запит. Щоб показати більше, потрібно у відповіді передати параметр `next_offset`, 
який дублюватиметься в полі `offset` у наступному `InlineQuery`. Так бот зрозуміє, що потрібно завантажити нові дані, 
починаючи з `offset`. А рядок це тому, що крім чисел можна використовувати якісь ідентифікатори, типу UUID.

### Формат вихідних відповідей {: id="outgoing-answer-format" }

Для відповіді на запити користувача існує рівно один метод: 
[answerInlineQuery](https://core.telegram.org/bots/api#answerinlinequery). 
Але [відправляємих типів](https://core.telegram.org/bots/api#inlinequeryresult) цілих 20. Точніше, 
насправді їх 11, оскільки решта — просто ті ж типи, але з іншими вхідними даними, наприклад, `file_id` 
замість посилання на медіафайл. Різні типи краще всього не змішувати один з одним, особливо Article з рештою.
Розглянемо деякі з них окремо.

![тип InlineQueryResultArticle](../images/ru/inline_mode/inline_articles.jpg)

Мабуть, найчастіше використовуваний тип — це [InlineQueryResultArticle](https://core.telegram.org/bots/api#inlinequeryresultarticle)
(на зображенні вверху). У всіх основних клієнтах виглядає як стос з прямокутних блоків, у яких завжди є 
заголовок, іноді присутній опис, а зліва відображається або картинка-превью, або просто заглушка. 
Якщо розробник встановив атрибут `url`, то деякі клієнти виводять вказане посилання під рядком опису, а 
превью стає кліквабельним і веде за самим посиланням прямо в браузер. При натисканні на рядок відправляється те, 
що встановлено в аргументі `input_message_content` (він обов'язковий), який може мати 5 різних типів:

* текст
* геолокація
* пам'ятка (venue)
* контакт
* рахунок для оплати (invoice)

![тип InlineQueryResultPhoto](../images/ru/inline_mode/inline_pictures.png)

Решта типів відносяться до т.зв. «медіафайлів», які ми розглянемо на прикладі зображень. При відповіді набором 
зображень дані вишикуються або вертикальними плитками, як на скриншоті вище, або прокручуваною горизонтальною 
полосою (наприклад, в iOS-версії). 

Якщо ви ще раз відкриєте розділ про [InlineQueryResult](https://core.telegram.org/bots/api#inlinequeryresult), то 
побачите, що Photo (як і деякі інші типи) представлено в двох варіантах: 
`InlineQueryResultPhoto` і `InlineQueryResultCachedPhoto`. Різниця в тому, що перший варіант приймає посилання 
на зображення з Інтернету, а другий — `file_id` від вже завантаженого в Telegram медіа.

!!! warning "Важливо"
    В інлайн-режимі не можна вивантажувати зображення прямо з файлу. Або посилання в Інтернеті, або `file_id`. 
    Третього не буває.

За замовчуванням, натиск на медіафайл зі списку результатів приводить до відправки цього медіа в викликаний чат. 
Однак якщо встановити аргумент `input_message_content` (у випадку з медіа він вже необов'язковий), то при натисканні буде 
відправлено те, що встановлено в цьому аргументі. Наприклад, натиск на обкладинку фільму відправить його текстовий опис 
зі посиланням на перегляд у онлайн-кінотеатрі. Або при натисканні на фото співробітника відправиться його телефонний номер як 
контакт 👀. До речі, незважаючи на те, що у медіа є аргументи `title` та `description`, клієнти їх не виводять, 
та й сам Bot API їх [ігнорує](https://t.me/tdlibchat/16432). 

У методу answerInlineQuery є кілька аргументів, на які потрібно звернути увагу. По-перше, це `cache_time`. 
Він визначає, на який період результат запиту може бути закешовано серверами телеграму, щоб не відправляти його в бота. 
Якщо ваші дані статичні або змінюються рідко, сміливо підвищуйте це значення. По-друге, прапорець `is_personal`, 
який впливає на те, буде чи закешовано результат тільки для одного користувача або одразу для всіх. Якщо ваш бот 
показує персоналізовані значення залежно від ID користувача, встановлюйте в True.

!!! info ""
    Автор цих рядків одного разу забув указати прапорець `is_personal` у його боті [@my_id_bot](https://t.me/my_id_bot), 
    встановив кеш на 86400 секунд (1 добу) і почув багато обурення від користувачів, які відправляли його ID замість своїх 
    власних. Навчайтеся на чужих помилках, не на своїх.

По-третє, рядковий аргумент `next_offset`, який дозволяє реалізовувати завантаження результатів при прокручуванні, оскільки 
в одній відповіді на InlineQuery можна повернути не більше 50 значень. Використання `next_offset` ми розглянемо у окремому 
прикладі.

По-четверте, `switch_pm_text` та `switch_pm_parameter`. Крім результатів запиту, бот може над ними показати маленьку 
кнопочку з текстом з аргументу `switch_pm_text`, натиск на яку аналогічно дипліну, тобто користувач перейде в 
особистий чат з ботом, замість поля введення буде кнопка «РОЗПОЧАТИ», а при натисканні боту прилетить повідомлення з текстом 
`/start ТЕКСТ`, де замість ТЕКСТ — значення аргументу `switch_pm_parameter`.

![Кнопка switch_pm](../images/ru/inline_mode/switch_pm_button.png)

Подібну штуку дуже зручно використовувати, якщо по конкретному запиту немає результатів або хочеться дати змогу 
користувачеві швидко щось додати. Є й ще одна фіча, але її ми розглянемо пізніше у процесі розробки бота. До речі, 
про нього... 

## Практика {: id="practice" }

Щоб бот знав, що потрібно показувати при виклику в інлайн-режимі, йому потрібні якісь дані: або попередньо збережені, 
або отримані від самого користувача. Як приклад напишемо бота, який буде приймати від користувача посилання 
та картинки, а потім показувати все це в інлайн-режимі за запитом.

!!! info ""
    Не забудьте включити інлайн-режим у бота через [@BotFather](https://t.me/botfather): 
    Bot Settings -> Inline Mode -> Turn on

### Система зберігання {: id="storage" }

Щоб не занурюватися сильно в деталі, тим більше, що цей розділ і так досить довгий, договоримось, що наш тестовий 
бот буде використовувати звичайний in-memory словник як імітацію бази даних. Це дозволить не заморочуватися 
по поводу скидання стану при відладці, а також спростить наповнення сховища заздалегідь, якщо ви вдруг захочете 
запускати бота одразу з готовими посиланнями або картинками. Для кожного з двох типів даних буде по три функції: 
додати дані, отримати дані, видалити дані. Власне, ось весь код файлу:

```python title="storage.py"
from typing import Optional

# У реальному житті тут має бути нормальна СУБД.
# Але для прикладу нам буде достатньо показати на звичайному словнику.
# Врахуйте, що він скидається при перезапуску бота.
data = dict()


def add_link(
        telegram_id: int,
        link: str,
        title: str,
        description: Optional[str]
):
    """
    Зберігає посилання у словник

    :param telegram_id: ID користувача в Telegram
    :param link: текст посилання
    :param title: заголовок посилання
    :param description: (опціонально) опис посилання
    """
    data.setdefault(telegram_id, dict())
    data[telegram_id].setdefault("links", dict())
    data[telegram_id]["links"][link] = {
        "title": title,
        "description": description
    }

def add_photo(
        telegram_id: int,
        photo_file_id: str,
        photo_unique_id: str
):
    """
    Зберігає зображення у словник

    :param telegram_id: ID користувача в Telegram
    :param photo_file_id: file_id зображення
    :param photo_unique_id: file_unique_id зображення
    """
    data.setdefault(telegram_id, dict())
    data[telegram_id].setdefault("images", [])
    if photo_file_id not in data[telegram_id]["images"]:
        data[telegram_id]["images"].append((photo_file_id, photo_unique_id))

def get_links_by_id(telegram_id: int) -> dict:
    """
    Отримує збережені посилання користувача

    :param telegram_id: ID користувача в Telegram
    :return: якщо по користувачеві є дані, то словник з посиланнями
    """
    if telegram_id in data and "links" in data[telegram_id]:
        return data[telegram_id]["links"]
    return dict()

def get_images_by_id(telegram_id: int) -> list[str]:
    """
    Отримує збережені зображення користувача

    :param telegram_id: ID користувача в Telegram
    :return:
    """
    if telegram_id in data and "images" in data[telegram_id]:
        return [item[0] for item in data[telegram_id]["images"]]
    return []

def delete_link(telegram_id: int, link: str):
    """
    Видаляє посилання

    :param telegram_id: ID користувача в Telegram
    :param link: посилання
    """
    if telegram_id in data:
        if "links" in data[telegram_id]:
            if link in data[telegram_id]["links"]:
                del data[telegram_id]["links"][link]

def delete_image(telegram_id: int, photo_file_unique_id: str):
    """
    Видаляє зображення

    :param telegram_id: ID користувача в Telegram
    :param photo_file_unique_id: file_unique_id зображення для видалення
    """
    if telegram_id in data and "images" in data[telegram_id]:
        for index, (_, unique_id) in enumerate(data[telegram_id]["images"]):
            if unique_id == photo_file_unique_id:
                data[telegram_id]["images"].pop(index)
```

### Команди у боті {: id="common-commands" }

У бота буде кілька загальних команд: `/start`, `/help`, `/save`, `/delete` та `/cancel`. Перші дві інформаційні, 
`/save` розпочинає процес збереження даних, `/delete` розпочинає процес видалення даних, а `/cancel`, відповідно, 
перериває один з запущених процесів. Почнемо з команди `/save`.

### Збереження даних {: id="data-saving" }

На цей раз ми опишемо стани (states) у окремому файлі, щоб було зручніше імпортувати. Для цього створимо файл 
`states.py` і реалізуємо клас `SaveCommon`, де буде один стан «чекає введення»:

```python title="states.py"
from aiogram.fsm.state import StatesGroup, State

class SaveCommon(StatesGroup):
    waiting_for_save_start = State()
```

Тепер займемося обробкою збереження повідомлень різних типів 

#### Текст {: id="save-text" }

Почнемо з текстових повідомлень. Ідея проста: користувач кидає повідомлення. Якщо там є хоча б одне посилання, то 
воно витягується, а далі пропонується ввести назву посилання (обов'язково) та опис. Останній крок можна пропустити 
командою `/skip`. Якщо посилань кілька, то береться тільки перше.

Крім описаного вище стану «чекає введення», буде ще два специфічні для тексту: «чекає введення заголовка» та 
«чекає введення опису». У `states.py` додамо ці стейти:

```python title="states.py"
# тут попередній код

class TextSave(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
```

Почнемо з двох хендлерів на текст у стейті `SaveCommon` -> `waiting_for_save_start`. Потрібно ловити повідомлення з посиланнями. 
У розділі [про фільтри та мідлвари](filters-and-middlewares.md#filters-as-classes) ми вже робили подібний фільтр, але для 
юзернеймів. Настав час його звідти скопіювати та адаптувати під посилання:

```python title="filters/text_has_link.py"
from typing import Union, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message


class HasLinkFilter(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        # Якщо entities вообще немає, повернеться None,
        # у цьому випадку вважаємо, що це порожній список
        entities = message.entities or []

        # Якщо є хоча б одне посилання, повертаємо його
        for entity in entities:
            if entity.type == "url":
                return {"link": entity.extract_from(message.text)}

        # Якщо нічого не знайшли, повертаємо None
        return False
```

Щоб скоротити імпорт, відредагуємо файл `filters/__init__.py`:

```python title="filters/__init__.py"
from .text_has_link import HasLinkFilter

# Робимо так, щоб потім просто імпортувати
# from filters import HasLinkFilter
__all__ = [
    "HasLinkFilter"
]
```

Чому хендлерів на текст потрібно два? Перший буде ловити повідомлення, де є посилання, а другий — де його нема. Пишемо:

```python title="handlers/save_text.py"
# <імпорти>

@router.message(SaveCommon.waiting_for_save_start, F.text, HasLinkFilter())
async def save_text_has_link(message: Message, link: str, state: FSMContext):
    await state.update_data(link=link)
    await state.set_state(TextSave.waiting_for_title)
    await message.answer(
        text=f"Окей, я знайшов у повідомленні посилання {link}. "
             f"Тепер відправ мені заголовок (не більше 30 символів)"
    )

@router.message(SaveCommon.waiting_for_save_start, F.text)
async def save_text_no_link(message: Message):
    await message.answer(
        text="Гм.. я не знайшов у твоєму повідомленні посилання. "
             "Спробуй ще раз або натисни /cancel, щоб скасувати."
    )
```

Далі очікуємо від користувача введення заголовка записи. Тут теж можна розбити логіку на два хендлери: для успішного 
та неуспішного збігу обставин:

```python title="handlers/save_text.py" hl_lines="3"
# імпорти та попередні кроки

@router.message(TextSave.waiting_for_title, F.text.func(len) <= 30)
async def title_entered_ok(message: Message, state: FSMContext):
    await state.update_data(title=message.text, description=None)
    await state.set_state(TextSave.waiting_for_description)
    await message.answer(
        text="Так, заголовок бачу. Тепер введи опис "
             "(теж не більше 30 символів) "
             "або натисни /skip, щоб пропустити цей крок"
    )

@router.message(TextSave.waiting_for_title, F.text)
async def too_long_title(message: Message):
    await message.answer("Занадто довгий заголовок. Спробуй ще раз")
    return
```

Зверніть увагу на код `F.text.func(len) <= 30`. Magic filter дозволяє передати на вхід якусь функцію, яка виконається над тим, що вказано до `.func`. Тобто `F.text.func(len)` -> `len(F.text)` та тільки якщо атрибут `.text` 
не є None (іншими словами, тут ще й перевірка на content-type). Але взагалі конкретно для `len()` 
є підтримка прямо в 
[magic-filter](https://github.com/aiogram/magic-filter/blob/3c5e38fd5cd359fd961e26bab17e65201b02c1c6/magic_filter/magic.py#L227-L228): 
`F.text.len() <= 30`

На черзі хендлер на опис. Тут можна знову розбити на два хендлери... стойте, але ж функція `too_long_title()`, 
по суті, може так само підходити й для кроку з описом, якщо у нас однакові ліміти на текст! Перейменуємо її та 
додамо фільтр на інший стейт:

```python title="handlers/save_text.py"
@router.message(TextSave.waiting_for_title, F.text)
@router.message(TextSave.waiting_for_description, F.text)
async def text_too_long(message: Message):  # колишня too_long_title()
    await message.answer("Занадто довгий заголовок. Спробуй ще раз")
    return
```

Тепер візьмемось за останній хендлер, у який потрапляємо або при введенні короткого опису, або за командою `/skip`. 
А раз потрібно ловити два входи, то вішаємо два декоратори, в аргументах приймаємо опціональний `CommandObject` та всередину 
дивимось: якщо команди нема, значить, ввели опис:

```python title="handlers/save_text.py"
# Ця функція має бути ПЕРЕД text_too_long() !
@router.message(TextSave.waiting_for_description, F.text.func(len) <= 30)
@router.message(TextSave.waiting_for_description, Command("skip"))
async def last_step(
        message: Message,
        state: FSMContext,
        command: Optional[CommandObject] = None
):
    if not command:
        await state.update_data(description=message.text)
    # Зберігаємо дані у нашу не-справжню БД
    data = await state.get_data()
    add_link(message.from_user.id, data["link"], data["title"], data["description"])

    await message.answer("Посилання збережено!")
    await state.clear()
```

Отже, ми зробили набір хендлерів для збереження посилань у нашу in-memory базу даних. Ось весь код файлу цілком:

```python title="handlers/save_text.py"
from typing import Optional

from aiogram import Router, F
from aiogram.filters.command import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from filters import HasLinkFilter
from states import SaveCommon, TextSave
from storage import add_link

router = Router()

@router.message(SaveCommon.waiting_for_save_start, F.text, HasLinkFilter())
async def save_text_has_link(message: Message, link: str, state: FSMContext):
    await state.update_data(link=link)
    await state.set_state(TextSave.waiting_for_title)
    await message.answer(
        text=f"Окей, я знайшов у повідомленні посилання {link}. "
             f"Тепер відправ мені опис (не більше 30 символів)"
    )

@router.message(SaveCommon.waiting_for_save_start, F.text)
async def save_text_no_link(message: Message):
    await message.answer(
        text="Гм.. я не знайшов у твоєму повідомленні посилання. "
             "Спробуй ще раз або натисни /cancel, щоб скасувати."
    )

@router.message(TextSave.waiting_for_title, F.text.func(len) <= 30)
async def title_entered_ok(message: Message, state: FSMContext):
    await state.update_data(title=message.text, description=None)
    await state.set_state(TextSave.waiting_for_description)
    await message.answer(
        text="Так, заголовок бачу. Тепер введи опис "
             "(теж не більше 30 символів) "
             "або натисни /skip, щоб пропустити цей крок"
    )

@router.message(TextSave.waiting_for_description, F.text.func(len) <= 30)
@router.message(TextSave.waiting_for_description, Command("skip"))
async def last_step(
        message: Message,
        state: FSMContext,
        command: Optional[CommandObject] = None
):
    if not command:
        await state.update_data(description=message.text)
    # Зберігаємо дані у нашу не-справжню БД
    data = await state.get_data()
    add_link(message.from_user.id, data["link"], data["title"], data["description"])
    await state.clear()
    kb = [[InlineKeyboardButton(
        text="Спробувати",
        switch_inline_query="links"
    )]]
    await message.answer(
        text="Посилання збережено!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )

@router.message(TextSave.waiting_for_title, F.text)
@router.message(TextSave.waiting_for_description, F.text)
async def text_too_long(message: Message):
    await message.answer("Занадто довгий заголовок. Спробуй ще раз")
    return
```

#### Зображення {: id="save-images" }

З картинками набагато простіше; вони додаються в один крок. Але є нюанс: крім `file_id` для подальшого відображення, 
нам потрібно зберігати `file_unique_id`, оскільки він знадобиться, коли ми дозволимо користувачеві видаляти збережені картинки:

```python title="handlers/save_images.py"
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, PhotoSize
from states import SaveCommon
from storage import add_photo

router = Router()

@router.message(SaveCommon.waiting_for_save_start, F.photo[-1].as_("photo"))
async def save_image(message: Message, photo: PhotoSize, state: FSMContext):
    add_photo(message.from_user.id, photo.file_id, photo.file_unique_id)
    await message.answer("Зображення збережено!")
    await state.clear()
```

### Відображення даних {: id="show-data" }

Окей, дані зберігати навчилися, тепер потрібно їх якось відобразити. Для цього бот має ловити апдейти з типом 
`inline_query`, а в хендлер прийде об'єкт типу [InlineQuery](https://core.telegram.org/bots/api#inlinequery). 
Договоримось, що на порожній запит (поки) нічого показувати не будемо, на запит `@bot links` покажемо список посилань, а 
на запит `@bot images` — картинки. Замість `@bot`, звичайно ж, буде юзернейм бота.

#### Текст {: id="show-text" }

Для відповіді текстовими повідомленнями нам потрібно зібрати список об'єктів з типом  
[InlineQueryResultArticle](https://core.telegram.org/bots/api#inlinequeryresultarticle). Усі необхідні 
(та навіть додаткові) дані у нас вже є:

![Вміст об'єкта InlineQueryResultArticle](../images/ru/inline_mode/article_content.png "Вміст об'єкта InlineQueryResultArticle")

Для аргументу `input_message_content` напишемо просту вкладену функцію, яка буде повертати текст з урахуванням наявності або 
відсутності опису:

```python
def get_message_text(
        link: str,
        title: str,
        description: Optional[str]
) -> str:
    text_parts = [f'{html.bold(html.quote(title))}']
    if description:
        text_parts.append(html.quote(description))
    text_parts.append("")  # додамо порожній рядок
    text_parts.append(link)
    return "\n".join(text_parts)
```

Тепер опишемо сам хендлер:

```python title="handlers/inline_mode.py"
@router.inline_query(F.query == "links")
async def show_user_links(inline_query: InlineQuery):

    # Ця функція просто збирає текст, який буде
    # відправлений при натисканні на варіант в інлайн-режимі
    def get_message_text():
        # ця вкладена функція описана вище ↑

    results = []
    for link, link_data in get_links_by_id(inline_query.from_user.id).items():
        # У фінальний масив пхаємо кожний запис
        results.append(InlineQueryResultArticle(
            id=link,  # посилання у нас унікальні, тому проблем не буде
            title=link_data["title"],
            description=link_data["description"],
            input_message_content=InputTextMessageContent(
                message_text=get_message_text(
                    link=link,
                    title=link_data["title"],
                    description=link_data["description"]
                ),
                parse_mode="HTML"
            )
        ))
    # Важливо указати is_personal=True!
    await inline_query.answer(results, is_personal=True)
```

Отримуємо в результаті (у другого запису був пропущений етап з описом `description`):

![Перегляд посилань](../images/ru/inline_mode/our_links_result.png "Перегляд посилань")

При натисканні вийде таке гарне повідомлення:

![Результат у чаті](../images/ru/inline_mode/our_links_result_in_chat.png "Результат у чаті")

#### Зображення {: id="show-images" }

З зображеннями трохи простіше, однак тут є нюанс: ми не можемо як ID конкретного варіанту використовувати 
`file_id` картинки, оскільки він довший за 64 байти (ліміт Bot API). Тому ми будемо використовувати порядковий номер 
елемента у масиві, сконвертований у рядок. В іншому коді дуже схожий на попередній:

```python title="handlers/inline_mode.py"
@router.inline_query(F.query == "images")
async def show_user_images(inline_query: InlineQuery):
    results = []
    for index, file_id in enumerate(get_images_by_id(inline_query.from_user.id)):
        # У фінальний масив пхаємо кожний запис
        results.append(InlineQueryResultCachedPhoto(
            id=str(index),  # індекс елемента у list
            photo_file_id=file_id
        ))
    # Важливо указати is_personal=True!
    await inline_query.answer(results, is_personal=True)
```

Ну й результат:

![Відображення картинок в інлайн-режимі](../images/ru/inline_mode/our_images_result.png "Відображення картинок в інлайн-режимі")

### Видалення даних {: id="delete-data" }

Збережено потрібно час від часу чистити. Так і ми хочемо дати змогу користувачеві видаляти накопичені посилання 
та/або картинки. Для цього зробимо обробник на команду `/delete`. Але примушувати користувача вводити юзернейм бота 
та писати `links` чи `images` ми не хочемо. Для цього під відповіддю на команду розташуємо дві кнопки. Одна відкриє 
інлайн-режим на перегляді посилань, інша — на перегляді зображень. 

Додамо в `states.py` новий клас:

```python title="states.py"
class DeleteCommon(StatesGroup):
    waiting_for_delete_start = State()
```

Тепер зробимо хендлер на команду `/delete`:

```python title="handlers/common.py" hl_lines="7 13"
# новий імпорт
from aiogram.filters.state import StateFilter

@router.message(Command("delete"), StateFilter(None))
async def cmd_delete(message: Message, state: FSMContext):
    kb = []
    kb.append([
        InlineKeyboardButton(
            text="Вибрати посилання",
            switch_inline_query_current_chat="links"
        )
    ])
    kb.append([
        InlineKeyboardButton(
            text="Вибрати зображення",
            switch_inline_query_current_chat="images"
        )
    ])
    await state.set_state(DeleteCommon.waiting_for_delete_start)
    await message.answer(
        text="Виберіть, що хочете видалити:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )
```

При натисканні на таку кнопку підставляється потрібне значення в інлайн-режим, що одразу відкриє список посилань або 
зображень (для демонстрації я тимчасово прибрав спливаюче меню, щоб були видні кнопки):

![Кнопка switch_inline_query_current_chat](../images/ru/inline_mode/cmd_delete.png "Кнопка switch_inline_query_current_chat")

Якби ми використовували просто `switch_inline_query` замість `switch_inline_query_current_chat`, то Telegram запропонував би 
обрати чат, у який користувач може писати, а потім підставив би вказаний текст там.

Залишилось написати роутер, який буде ловити запити на видалення та редагувати вміст сховища:

```python title="handlers/delete_data.py"
# імпорти
router = Router()

@router.message(
    DeleteCommon.waiting_for_delete_start,
    F.text,
    ViaBotFilter(),
    HasLinkFilter()
)
async def link_deletion_handler(message: Message, link: str, state: FSMContext):
    delete_link(message.from_user.id, link)
    await state.clear()
    await message.answer(
        text="Посилання видалено! "
             "Видача інлайн-режиму оновиться протягом кількох хвилин.")

@router.message(
    DeleteCommon.waiting_for_delete_start,
    F.photo[-1].file_unique_id.as_("file_unique_id"),
    ViaBotFilter()
)
async def image_deletion_handler(
        message: Message,
        state: FSMContext,
        file_unique_id: str
):
    delete_image(message.from_user.id, file_unique_id)
    await state.clear()
    await message.answer(
        text="Зображення видалено! "
             "Видача інлайн-режиму оновиться протягом кількох хвилин.")
```

Зверніть увагу: зображення ми видаляємо за `file_unique_id`, оскільки при кожній відправці картинки `file_id` 
буде різний (якщо коротко: у повному `file_id` зашиті відмітки часу та інші непостійні дані).


### Switch туди й назад {: id="switch-parameter" }

Коли ми раніше обговорювали [формат вихідних відповідей](#outgoing-answer-format), то бачили аргументи 
з префіксом `switch_pm`. Давайте їх використаємо, щоб користувач міг одразу перейти до додавання даних з будь-якого 
чату, а не тільки з особистого чату з ботом.

Додамо в обробник інлайн-запитів вищевказані параметри. Для цього перепишемо виклик методу `answer_inline_query()` 
у файлі `handlers/inline_mode.py`:

```python
await inline_query.answer(
        results, is_personal=True,
        switch_pm_text="Додати ще »»",
        switch_pm_parameter="add"
    )
```

У файлі `handlers/common.py` хендлеру на команду `/save` додамо ще одну точку входу через фільтр `CommandStart` 
з диплінком `add`:

```python title="handlers/common.py" hl_lines="4"
# новий імпорт:
from aiogram.filters.command import CommandStart

@router.message(CommandStart(magic=F.args == "add"))
@router.message(Command("save"), StateFilter(None))
async def cmd_save(message: Message, state: FSMContext):
    ...

# Врахуйте, що хендлер на просто /start має йти ПІЗНІШЕ
@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    ...
```

А також на останньому етапі додавання тексту та картинок додамо `switch_inline_query` кнопку з пропозицією 
спробувати скинути щось в інший чат:

```python
# файл handlers/save_text.py
@router.message(TextSave.waiting_for_description, F.text.func(len) <= 30)
@router.message(TextSave.waiting_for_description, Command("skip"))
async def last_step(...):
    # тут решта коду функції
    kb = [[InlineKeyboardButton(
        text="Спробувати",
        switch_inline_query="links"
    )]]
    await message.answer(
        text="Посилання збережено!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )

# файл handlers/save_images.py
@router.message(SaveCommon.waiting_for_save_start, F.photo[-1].as_("photo"))
async def save_image(...):
    # тут решта коду функції
    kb = [[InlineKeyboardButton(
        text="Спробувати",
        switch_inline_query="images"
    )]]
    await message.answer(
        text="Зображення збережено!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )
```

І тут криється ще одна цікава фіча інлайн-режиму: якщо ви викличете бота не в ЛС з ним, перейдете за кнопкою 
"Додати ще »»", і дійдете до останнього кроку, то коли бот відправить повідомлення зі `switch_inline_query`-кнопкою, 
клієнт Telegram автоматично поверне користувача в исходний чат та одразу відкриє інлайн-режим з потрібним текстом!


## Додаткові матеріали {: id="extras" }

### Завантаження результатів {: id="lazy-loading" }

Відповідно до документації Bot API, в одному виклику [answerInlineQuery](https://core.telegram.org/bots/api#answerinlinequery) 
можна відправити не більше 50 елементів. А якщо потрібно більше? На цей випадок знадобиться параметр `next_offset`. Його 
указує сам бот, і це ж значення прийде у наступному інлайн-запиті, коли користувач пролистає всю поточну пачку. 
Для прикладу напишемо простий генератор чисел, який повертає пачки по 50 елементів, але з максимальним значенням 195:

```python title="handlers/inline_pagination_demo.py"
def get_fake_results(start_num: int, size: int = 50) -> list[int]:
    """
    Генерує список послідовних чисел

    :param start_num: стартове число для генератора
    :param size: розмір пачки (за замовч. 50)
    :return: список послідовних чисел
    """
    overall_items = 195
    # Якщо результатів більше немає, відправляємо порожній список
    if start_num >= overall_items:
        return []
    # Відправка неповної пачки (останньої)
    elif start_num + size >= overall_items:
        return list(range(start_num, overall_items+1))
    else:
        return list(range(start_num, start_num+size))
```

Тепер напишемо інлайн-хендлер таким чином, щоб при наближенні до кінця поточного списку Telegram запитував  
продовження. Для цього на початку перевіряємо поле `offset` та встановлюємо його рівним одиниці, якщо воно порожне. Далі генеруємо 
фейковий список результатів. Якщо на виході рівно 50 об'єктів, то у відповіді указуємо `next_offset` рівний поточному 
значенню + 50. Якщо об'єктів менше, то нічого не указуємо, щоб Telegram більше не намагався завантажити нові рядки:

```python title="handlers/inline_pagination_demo.py" hl_lines="21"
@router.inline_query(F.query == "long")
async def pagination_demo(
        inline_query: InlineQuery,
):
    # Розраховуємо offset як число
    offset = int(inline_query.offset) if inline_query.offset else 1
    results = [InlineQueryResultArticle(
        id=str(item_num),
        title=f"Об'єкт №{item_num}",
        input_message_content=InputTextMessageContent(
            message_text=f"Об'єкт №{item_num}"
        )
    ) for item_num in get_fake_results(offset)]
    if len(results) < 50:
        await inline_query.answer(
            results, is_personal=True
        )
    else:
        await inline_query.answer(
            results, is_personal=True, 
            next_offset=str(offset+50)
        )
```

По мірі листання інлайн-результатів, бот буде отримувати запити та повертати все нові й нові результати, поки не дійде 
до 195-го елемента, далі запити припиняться.

### Збір статистики {: id="inline-feedback" }

Мало хто знає, але Telegram дозволяє збирати просту статистику за використанням бота в інлайн-режимі. Для початку 
потрібно включити відповідну налаштування у @BotFather: `/mybots` - (вибрати бота) - Bot Settings - Inline Feedback:

![Приклад роботи бота @imdb в інлайн-режимі](../images/ru/inline_mode/botfather_inline_feedback.png "Приклад роботи бота @imdb в інлайн-режимі")

Числа на кнопках означають _ймовірність_ отримання події [ChosenInlineResult](https://core.telegram.org/bots/api#choseninlineresult) 
при виборі користувачем якогось об'єкта в інлайн-режимі. Так, наприклад, якщо встановлено значення **10%**, то при 
кожному виборі об'єкта існує ймовірність у десять відсотків отримати подію ChosenInlineResult у боті. Встановлювати 
значення 100% Telegram не рекомендує через подвоєння навантаження на бота. Таким чином, для якої-небудь серйозної аналітики 
подібна фіча не підходить, але у вмілих руках і за великий період часу може дати загальне уявлення про найбільш 
корисні інлайн-результати. Приклад хендлера на подібні події:

```python title="handlers/inline_chosen_result_demo.py"
from aiogram import Router
from aiogram.types import ChosenInlineResult

router = Router()

@router.chosen_inline_result()
async def pagination_demo(
        chosen_result: ChosenInlineResult,
):
    # Пишемо прямо на екран. Але, можливо, ви захочете зберігати куди-небудь
    print(
        f"After '{chosen_result.query}' query, "
        f"user chose option with ID '{chosen_result.result_id}'"
    )
```

Незважаючи на те, що телеграм не рекомендує встановлювати великі значення для Inline Feedback, у цієї штуки є як 
мінімум одне практичне застосування: деякі музичні боти намагаються завантажити повну версію композиції за запитом, 
не зберігаючи пісню заздалегідь. Якщо це робити у момент виклику бота в інлайн-режимі, можна не вкластися в 10-15 секунд, 
по закінченню яких Bot API повертає помилку про «прогірклу» апдейт.

І ось як виручаються розробники: поки бот шукає трек, у попередньому прослуховуванні пропонується короткий сэмпл 
(5-10 секунд). Коли користувач жме на якусь рядок, відправляється аудіоповідомлення з прикріпленою інлайн-кнопкою
(інакше не можна редагувати повідомлення), бот ловить подію відправки, витягує з апдейту з типом `ChozenInlineResult` 
наскрізний `inline_message_id` повідомлення, грузить повну версію аудіо та, використовуючи цей `inline_message_id` редагує 
сэмпл на повноцінний трек. Telegram приучає до костилів, так. 

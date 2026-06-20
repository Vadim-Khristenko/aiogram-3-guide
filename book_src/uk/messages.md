---
title: Робота з повідомленнями
description: Робота з повідомленнями
---

# Робота з повідомленнями

!!! info ""
    Використовувана версія aiogram: 3.7.0

У цій главі ми розберемось, як застосовувати різні типи форматування до повідомлень та працювати з медіафайлами.

## Текст {: id="text" }
Обробка текстових повідомлень — це, мабуть, одна з найважливіших дій у більшості ботів. Текстом можна виразити 
практично що завгодно і при цьому подавати інформацію хочеться _красиво_. У розпорядженні розробника є три способи 
розмітки тексту: HTML, Markdown та MarkdownV2. Найбільш просунутими з них вважаються HTML та MarkdownV2, «класичний» 
Markdown підтримує менше можливостей і більше не використовується в aiogram.

Перш, ніж ми розглянемо способи роботи з текстом в aiogram, необхідно згадати 
важливу відмінність aiogram 3.x від 2.x: у «двійці» за замовчуванням обробляли тільки 
текстові повідомлення, а в «тройці» — будь-якого типу. Якщо точніше, ось як тепер потрібно 
приймати виключно текстові повідомлення:

```python
# було (декоратором)
@dp.message_handler()
async def func_name(...)

# було (функцією-реєстратором)
dp.register_message_handler(func_name)

# стало (декоратором)
from aiogram import F
@dp.message(F.text)
async def func_name(...)

# стало (функцією-реєстратором)
dp.message.register(func_name, F.text)
```

Про «магічний фільтр» **F** ми поговоримо в [іншій главі](filters-and-middlewares.md).

### Форматований вивід {: id="formatting-options" }

За вибір форматування при відправці повідомлень відповідає аргумент `parse_mode`, наприклад:
```python
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode

# Якщо не вказати фільтр F.text, 
# то хендлер спрацює навіть на картинку з підписом /test
@dp.message(F.text, Command("test"))
async def any_message(message: Message):
    await message.answer(
        "Hello, <b>world</b>!", 
        parse_mode=ParseMode.HTML
    )
    await message.answer(
        "Hello, *world*\!", 
        parse_mode=ParseMode.MARKDOWN_V2
    )
```

![Hello world з різним форматуванням](../images/ru/messages/l02_1.png)

Якщо в боті скрізь використовується певне форматування, то кожен раз вказувати аргумент `parse_mode` досить 
обтяжливо. На щастя, в aiogram можна задати параметри бота за замовчуванням. Для цього створіть об'єкт `DefaultBotProperties` 
і передайте туди потрібні налаштування:

```python
from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token="123:abcxyz",
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
        # тут ще багато інших цікавих налаштувань
    )
)

# де-небудь у функції...
await message.answer("Повідомлення з <u>HTML-розміткою</u>")
# щоб явно вимкнути форматування в конкретному запиті, 
# передайте parse_mode=None
await message.answer(
    "Повідомлення без <s>якої-либо розмітки</s>", 
    parse_mode=None
)
```

![Налаштування типу розмітки за замовчуванням](../images/ru/messages/l02_2.png)

### Екранування введення {: id="input-escaping" }

Часто трапляються ситуації, коли остаточний текст повідомлення бота наперед невідомий 
і формується виходячи з деяких зовнішніх даних: ім'я користувача, його введення тощо. 
Напишемо хендлер на команду `/hello`, який буде привітати користувача за його повним іменем
(`first_name + last_name`), наприклад: «Hello, Іван Іванов»:

```python
from aiogram.filters import Command

@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    await message.answer(
        f"Hello, <b>{message.from_user.full_name}</b>",
        parse_mode=ParseMode.HTML
    )
```

І здається все добре, бот вітає користувачів:

![Робота команди /hello](../images/ru/messages/cmd_hello_before.png)

Але тут приходить юзер з іменем &lt;Славик777&gt; і бот мовчить! А в логах видно наступне:
`aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: can't parse entities: 
Unsupported start tag "Славик777" at byte offset 7`

Упс, у нас стоїть режим форматування HTML, і Telegram намагається спарсити &lt;Славик777&gt; як HTML-тег. Що ж. 
Але у цієї проблеми є кілька рішень. Перше: екранувати передаючи значення.

```python
from aiogram import html
from aiogram.filters import Command

@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    await message.answer(
        f"Hello, {html.bold(html.quote(message.from_user.full_name))}",
        parse_mode=ParseMode.HTML
    )
```

Друге трохи складніше, але більш просунуте: скористатися спеціальним інструментом, який буде 
збирати окремо текст і окремо інформацію про те, які його куски повинні бути відформатовані.

```python
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold

@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    content = Text(
        "Hello, ",
        Bold(message.from_user.full_name)
    )
    await message.answer(
        **content.as_kwargs()
    )
```

У прикладі вище конструкція `**content.as_kwargs()` повернула аргументи `text`, `entities`, `parse_mode` і 
підставить їх у виклик `answer()`.

![Робота команди /hello після виправлень](../images/ru/messages/cmd_hello_after.png)

Згаданий інструмент форматування досить комплексний, 
[офіційна документація](https://docs.aiogram.dev/en/latest/utils/formatting.html) демонструє зручне відображення 
складних конструкцій, наприклад:

```python
from aiogram.filters import Command
from aiogram.utils.formatting import (
    Bold, as_list, as_marked_section, as_key_value, HashTag
)

@dp.message(Command("advanced_example"))
async def cmd_advanced_example(message: Message):
    content = as_list(
        as_marked_section(
            Bold("Success:"),
            "Test 1",
            "Test 3",
            "Test 4",
            marker="✅ ",
        ),
        as_marked_section(
            Bold("Failed:"),
            "Test 2",
            marker="❌ ",
        ),
        as_marked_section(
            Bold("Summary:"),
            as_key_value("Total", 4),
            as_key_value("Success", 3),
            as_key_value("Failed", 1),
            marker="  ",
        ),
        HashTag("#test"),
        sep="\n\n",
    )
    await message.answer(**content.as_kwargs())
```

![Просунутий приклад](../images/ru/messages/advanced_example.png)

!!! info ""
    Докладніше про різні способи форматування та підтримувані теги можна дізнатися 
    [у документації Bot API](https://core.telegram.org/bots/api#formatting-options).

### Збереження форматування {: id="keep-formatting" }

Уявимо, що бот повинен отримати форматований текст від користувача і додати туди щось 
своє, наприклад, мітку часу. Напишемо простий код:

```python
# новий імпорт!
from datetime import datetime

@dp.message(F.text)
async def echo_with_time(message: Message):
    # Отримуємо поточний час у часовому поясі ПК
    time_now = datetime.now().strftime('%H:%M')
    # Створюємо підкреслений текст
    added_text = html.underline(f"Створено в {time_now}")
    # Відправляємо нове повідомлення з доданим текстом
    await message.answer(f"{message.text}\n\n{added_text}", parse_mode="HTML")
```

![Доданий текст (невдала спроба)](../images/ru/messages/keep_formatting_bad.png)

Гм, щось пішло не так, чому збилось форматування вихідного повідомлення? 
Це відбувається тому, що `message.text` повертає просто текст, без будь-яких оформлень. 
Щоб отримати текст у потрібному форматуванні, скористаємось альтернативними властивостями: 
`message.html_text` або `message.md_text`. Сейчас нам потрібен перший варіант. Замінюємо у прикладі 
вище `message.text` на `message.html_text` і отримуємо коректний результат:

![Доданий текст (успіх)](../images/ru/messages/keep_formatting_good.png)

### Робота з entities {: id="message-entities" }

Telegram сильно спрощує життя розробникам, виконуючи попередню обробку повідомлень користувачів на своєму боці. 
Наприклад, деякі сутності, типу e-mail, номера телефону, імені користувача та ін. можна не доставати 
[регулярними виразами](https://uk.wikipedia.org/wiki/Регулярні_вирази), а витягнути 
прямо з об'єкту [Message](https://core.telegram.org/bots/api#message) та поля 
`entities`, що містить масив об'єктів типу 
[MessageEntity](https://core.telegram.org/bots/api#messageentity). Як приклад напишемо 
хендлер, який витягує посилання, e-mail та моноширинний текст зі повідомлення (по одній штуці).  
Тут криється важливий підводний камінь. **Telegram повертає не самі значення, а їх початок у тексті та довжину**. 
Більше того, текст вважається в символах UTF-8, а entities працюють з UTF-16, через це, якщо просто взяти 
позицію та довжину, то при наявності UTF-16 символів (наприклад, емодзі) ваш оброблений текст просто зрушиться. 

Найкраще це демонструє приклад нижче. На скриншоті перша відповідь бота є результатом парсингу «в лоб», 
а друга — результат застосування аіограмного методу `extract_from()` над entity. На вхід йому передається весь вихідний текст:

```python
@dp.message(F.text)
async def extract_data(message: Message):
    data = {
        "url": "<N/A>",
        "email": "<N/A>",
        "code": "<N/A>"
    }
    entities = message.entities or []
    for item in entities:
        if item.type in data.keys():
            # Неправильно
            # data[item.type] = message.text[item.offset : item.offset+item.length]
            # Правильно
            data[item.type] = item.extract_from(message.text)
    await message.reply(
        "Ось що я знайшов:\n"
        f"URL: {html.quote(data['url'])}\n"
        f"E-mail: {html.quote(data['email'])}\n"
        f"Пароль: {html.quote(data['code'])}"
    )
```

![Парсинг entities](../images/ru/messages/parse_entities.png)

### Команди та їх аргументи {: id="commands-args" }

Telegram [надає](https://core.telegram.org/bots/features#inputs) користувачам безліч способів введення 
інформації. Одним з них є команди: ключові слова, що починаються зі слеша, наприклад, `/new` або `/ban`. 
Іноді бот може бути спроектований так, щоб чекати після самої команди якісь _аргументи_, типу `/ban 2d` або 
`/settimer 20h This is delayed message`. У складі aiogram є фільтр `Command()`, який спрощує життя розробнику. 
Реалізуємо останній приклад у коді:

```python
@dp.message(Command("settimer"))
async def cmd_settimer(
        message: Message,
        command: CommandObject
):
    # Якщо не передані ніякі аргументи, то
    # command.args буде None
    if command.args is None:
        await message.answer(
            "Помилка: не передані аргументи"
        )
        return
    # Намагаємось розділити аргументи на дві частини по першому пробілу
    try:
        delay_time, text_to_send = command.args.split(" ", maxsplit=1)
    # Якщо вийшло менше двох частин, вилетить ValueError
    except ValueError:
        await message.answer(
            "Помилка: неправильний формат команди. Приклад:\n"
            "/settimer <time> <message>"
        )
        return
    await message.answer(
        "Таймер додано!\n"
        f"Час: {delay_time}\n"
        f"Текст: {text_to_send}"
    )
```

Спробуємо передати команду з різними аргументами (або взагалі без них) та перевірити реакцію:

![Аргументи команд](../images/ru/messages/command_args.png)

З командами може виникнути невелика проблема в групах: Telegram автоматично підсвічує команди, що починаються 
зі слеша, через що часом трапляється от таке (дякую моїм дорогим підписникам за допомогу у створенні скриншота):

![Флуд командами](../images/ru/messages/commands_flood.png)

Щоб цього уникнути, можна змусити бота реагувати на команди з іншими префіксами. Вони не будуть підсвічуватися і 
потребуватимуть повністю ручного введення, тому самі оцінюйте корисність такого підходу.

```python
@dp.message(Command("custom1", prefix="%"))
async def cmd_custom1(message: Message):
    await message.answer("Бачу команду!")


# Можна вказати кілька префіксів....vv...
@dp.message(Command("custom2", prefix="/!"))
async def cmd_custom2(message: Message):
    await message.answer("І цю також бачу!")
```

![Кастомні префікси](../images/ru/messages/command_custom_prefix.png)

Проблема кастомних префіксів у групах тільки в тому, що боти-неадміни з увімкненим Privacy Mode (за замовчуванням) можуть 
не побачити такі команди через [особливості](https://core.telegram.org/bots/faq#what-messages-will-my-bot-get) 
логіки сервера. Найчастіший use-case — боти-модератори груп, які вже є адміністраторами.

### Дипліни {: id="deeplinks" }

Існує одна команда в Telegram, у якої є трохи більше можливостей. Це `/start`. Справа в тому, що можна 
сформувати посилання виду `t.me/bot?start=xxx` і при переході за таким посиланням користувачеві покажуть кнопку «Почати», при 
натиску якої бот отримає повідомлення `/start xxx`. Тобто у посиланні зашивається якийсь додатковий параметр, що не потребує 
ручного введення. Це називається дипліні (не плутати з дикпіком) і може використовуватися для купи різних речей: шорткати для 
активації різних команд, реферальна система, швидка конфігурація бота тощо. Напишемо два приклади:

```python
import re
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart

@dp.message(Command("help"))
@dp.message(CommandStart(
    deep_link=True, magic=F.args == "help"
))
async def cmd_start_help(message: Message):
    await message.answer("Це повідомлення зі справкою")


@dp.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r'book_(\d+)'))
))
async def cmd_start_book(
        message: Message,
        command: CommandObject
):
    book_number = command.args.split("_")[1]
    await message.answer(f"Sending book №{book_number}")
```

![Приклади диплінів](../images/ru/messages/deeplinks.png)

Врахуйте, що дипліни через `start` відправляють користувача в особистий чат з ботом. Щоб обрати групу та відправити дипліні туди, 
замініть `start` на `startgroup`. Також у aiogram існує зручна 
[функція](https://github.com/aiogram/aiogram/blob/228a86afdc3c594dd9db9e82d8d6d445adb5ede1/aiogram/utils/deep_linking.py#L126-L158) 
для створення диплінів прямо з вашого коду.

!!! tip "Більше диплінів, але не для ботів"
    У документації Telegram є докладний опис всевозможних диплінів для клієнтських додатків: 
    [https://core.telegram.org/api/links](https://core.telegram.org/api/links)


### Попередній перегляд посилань {: id="link-previews" }

Зазвичай при відправці текстового повідомлення з посиланнями Telegram намагається знайти та показати попередній перегляд першого за порядком посилання. 
Це поведінка можна налаштувати на свій розсуд, передавши як аргумент `link_preview_options` методу `send_message()` 
об'єкт `LinkPreviewOptions`:

```python
# Новий імпорт
from aiogram.types import LinkPreviewOptions

@dp.message(Command("links"))
async def cmd_links(message: Message):
    links_text = (
        "https://nplus1.ru/news/2024/05/23/voyager-1-science-data"
        "\n"
        "https://t.me/telegram"
    )
    # Посилання вимкнено
    options_1 = LinkPreviewOptions(is_disabled=True)
    await message.answer(
        f"Немає попереднього перегляду посилань\n{links_text}",
        link_preview_options=options_1
    )

    # -------------------- #

    # Малий попередній перегляд
    # Для використання prefer_small_media обов'язково вказувати ще й url
    options_2 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_small_media=True
    )
    await message.answer(
        f"Малий попередній перегляд\n{links_text}",
        link_preview_options=options_2
    )

    # -------------------- #

    # Великий попередній перегляд
    # Для використання prefer_large_media обов'язково вказувати ще й url
    options_3 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_large_media=True
    )
    await message.answer(
        f"Великий попередній перегляд\n{links_text}",
        link_preview_options=options_3
    )

    # -------------------- #

    # Можна поєднувати: малий попередній перегляд і розташування над текстом
    options_4 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_small_media=True,
        show_above_text=True
    )
    await message.answer(
        f"Малий попередній перегляд над текстом\n{links_text}",
        link_preview_options=options_4
    )

    # -------------------- #

    # Можна обрати, яке посилання буде використовуватися для попереднього перегляду,
    options_5 = LinkPreviewOptions(
        url="https://t.me/telegram"
    )
    await message.answer(
        f"Попередній перегляд не першого посилання\n{links_text}",
        link_preview_options=options_5
    )
```

Результат: 
![Приклади попередніх переглядів посилань](../images/ru/messages/link_preview_options.png)

Також деякі параметри попереднього перегляду можна вказати за замовчуванням у `DefaultBotProperties`, про що розповідалось 
на початку глави.

## Медіафайли {: id="media" }

### Відправка файлів {: id="uploading-media" }

Крім звичайних текстових повідомлень Telegram дозволяє обмінюватися медіафайлами різних типів: фото, відео, гіфки, 
геолокації, наклейки тощо. У більшості медіафайлів є властивості `file_id` та `file_unique_id`. Перший можна використовувати 
для повторної відправки одного й того ж файлу багато разів, причому відправка буде миттєвою, оскільки сам файл вже лежить 
на серверах Telegram. Це найпереважніший спосіб.  
Наприклад, наступний код змусить бота миттєво відповісти користувачеві тією ж гіфкою, яка була прислана: 

```python
@dp.message(F.animation)
async def echo_gif(message: Message):
    await message.reply_animation(message.animation.file_id)
```

!!! warning "Завжди використовуйте правильні file_id!"
    Бот повинен використовувати для відправки **тільки** ті `file_id`, які отримав напрямо сам, 
    наприклад, у особистому чаті від користувача або «побачивши» медіафайл у групі/каналі. При цьому, 
    якщо спробувати використати `file_id` від іншого бота, то це _може спрацювати_, але 
    через деякий час ви отримаєте помилку **wrong url/file_id specified**. Тому — 
    тільки свої `file_id`!

На відміну від `file_id`, ідентифікатор `file_unique_id` не можна використовувати для повторної відправки 
або скачування медіафайлу, але зате він однаковий у всіх ботів для конкретного медіа. 
Потрібен `file_unique_id` зазвичай тоді, коли кільком ботам потрібно знати, що їх власні `file_id` відносяться 
до одного й того ж файлу.

Якщо файл ще не існує на сервері Telegram, бот може завантажити його трьома різними 
способами: як файл у файловій системі, за посиланням і безпосередньо набір байтів. 
Для прискорення відправки і в цілому для більш бережного ставлення до серверів месенджера,
завантаження (upload) файлів Telegram правильніше виробляти один раз, а надалі використовувати `file_id`, 
який буде доступний після першого завантаження медіа. 

В aiogram 3.x присутні 3 класи для відправки файлів і медіа - `FSInputFile`, `BufferedInputFile`, 
`URLInputFile`, з ними можна ознайомитись 
в [документації](https://docs.aiogram.dev/en/dev-3.x/api/upload_file.html).

Розглянемо простий приклад відправки зображень усіма різними способами:
```python
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile

@dp.message(Command('images'))
async def upload_photo(message: Message):
    # Сюди будемо помістити file_id відправлених файлів, щоб потім ними скористатися
    file_ids = []

    # Щоб продемонструвати BufferedInputFile, скористаємось «класичним»
    # відкриттям файлу через `open()`. Але, взагалі кажучи, цей спосіб
    # найкраще підходить для відправки байтів з оперативної пам'яті
    # після проведення деяких маніпуляцій, наприклад, редагування через Pillow
    with open("buffer_emulation.jpg", "rb") as image_from_buffer:
        result = await message.answer_photo(
            BufferedInputFile(
                image_from_buffer.read(),
                filename="image from buffer.jpg"
            ),
            caption="Зображення з буфера"
        )
        file_ids.append(result.photo[-1].file_id)

    # Відправка файлу з файлової системи
    image_from_pc = FSInputFile("image_from_pc.jpg")
    result = await message.answer_photo(
        image_from_pc,
        caption="Зображення з файлу на комп'ютері"
    )
    file_ids.append(result.photo[-1].file_id)

    # Відправка файлу за посиланням
    image_from_url = URLInputFile("https://picsum.photos/seed/groosha/400/300")
    result = await message.answer_photo(
        image_from_url,
        caption="Зображення за посиланням"
    )
    file_ids.append(result.photo[-1].file_id)
    await message.answer("Відправлені файли:\n"+"\n".join(file_ids))
```

Підпис у фото, відео та GIF можна перенести нагору: 

```python
@dp.message(Command("gif"))
async def send_gif(message: Message):
    await message.answer_animation(
        animation="<file_id гіфки>",
        caption="Я сьогодні:",
        show_caption_above_media=True
    )
```

![підпис над анімацією](../images/ru/messages/caption_above_media.jpg)

### Скачування файлів {: id="downloading-media" }

Крім переможення для відправки, бот може скачати медіа собі на комп'ютер/сервер. Для цього у об'єкту типу `Bot` 
є метод `download()`. У прикладах нижче файли скачуються відразу у файлову систему, але ніхто не заважає 
замість цього зберегти в об'єкт BytesIO в пам'яті, щоб передати у якийсь додаток далі 
(наприклад, pillow). 

```python
@dp.message(F.photo)
async def download_photo(message: Message, bot: Bot):
    await bot.download(
        message.photo[-1],
        destination=f"/tmp/{message.photo[-1].file_id}.jpg"
    )


@dp.message(F.sticker)
async def download_sticker(message: Message, bot: Bot):
    await bot.download(
        message.sticker,
        # для Windows шляхи треба підправити
        destination=f"/tmp/{message.sticker.file_id}.webp"
    )
```

У випадку з зображеннями ми використали не `message.photo`, а `message.photo[-1]`, чому? 
Фотографії в Telegram у повідомленні приходять відразу в кількох екземплярах; це одне й те ж 
зображення з різним розміром. Відповідно, якщо ми беремо останній елемент (індекс -1), 
то працюємо з максимально доступним розміром фото.

!!! info "Скачування великих файлів"
    Боти, що використовують Telegram Bot API, можуть скачувати файли розміром не більше [20 мегабайт](https://core.telegram.org/bots/api#getfile). 
    Якщо ви плануєте скачувати/заливати великі файли, краще розглянути бібліотеки, що взаємодіють з 
    Telegram Client API, а не з Telegram Bot API, наприклад, [Telethon](https://docs.telethon.dev/en/latest/index.html) 
    або [Pyrogram](https://docs.pyrogram.org/).  
    Не багато хто знає, але Client API можуть використовувати не тільки звичайні аккаунти, але й 
    [боти](https://docs.telethon.dev/en/latest/concepts/botapi-vs-mtproto.html).
    
    А починаючи з Bot API версії 5.0, можна використовувати 
    [власний сервер Bot API](https://core.telegram.org/bots/api#using-a-local-bot-api-server) для роботи з 
    великими файлами.

### Альбоми {: id="albums" }

То, що ми називаємо «альбомами» (медіагрупами) у Telegram, насправді окремі повідомлення з медіа, у яких є спільний 
`media_group_id` і які візуально «склеюються» на клієнтах. Починаючи з версії 3.1, в aiogram є 
[«збирач» альбомів](https://docs.aiogram.dev/en/latest/utils/media_group.html), роботу з яким ми сейчас розглянемо. 
Але перш варто згадати кілька особливостей медіагруп:

* До них не можна прицепити інлайн-клавіатуру або відправити reply-клавіатуру разом з ними. Ніяк. Взагалі ніяк.
* У кожного медіафайлу в альбомі може бути своя підпис (caption). Якщо підпис є тільки у одного медіа, 
то вона буде виводитись як загальна підпис до всього альбому.
* Фотографії можна відправляти перемішано з відео в одному альбомі, файли (Document) та музика (Audio) не можна ні з чим 
змішувати, тільки з медіа того ж типу.
* В альбомі може бути не більше 10 (десяти) медіафайлів.

Тепер подивимось, як це зробити в aiogram:

```python
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message
from aiogram.utils.media_group import MediaGroupBuilder

@dp.message(Command("album"))
async def cmd_album(message: Message):
    album_builder = MediaGroupBuilder(
        caption="Загальна підпис для майбутнього альбому"
    )
    album_builder.add(
        type="photo",
        media=FSInputFile("image_from_pc.jpg")
        # caption="Підпис до конкретного медіа"

    )
    # Якщо ми відразу знаємо тип, то замість загального add
    # можна відразу викликувати add_<тип>
    album_builder.add_photo(
        # Для посилань або file_id достатньо відразу вказати значення
        media="https://picsum.photos/seed/groosha/400/300"
    )
    album_builder.add_photo(
        media="<ваш file_id>"
    )
    await message.answer_media_group(
        # Не забудьте викликати build()
        media=album_builder.build()
    )
```

Результат: 

![Результат роботи білдера](../images/ru/messages/media_group_builder.png)

А ось зі скачуванням альбомів все набагато гірше... Як уже було сказано вище, альбоми — це просто згруповані 
окремі повідомлення, а це значить, що боту вони прилітають також у різних апдейтах. Навряд чи існує 100% надійний 
спосіб прийняти весь альбом одним куском, але можна спробувати зробити це з мінімальними втратами. Зазвичай це робиться 
через мідлвер, мою власну реалізацію прийому медіагруп можна знайти 
[за цим посиланням](https://github.com/MasterGroosha/telegram-feedback-bot-topics/blob/master/bot/middlewares/albums_collector.py).

## Сервісні (служебні) повідомлення {: id="service" }

Повідомлення в Telegram діляться на текстові, медіафайли та служебні (вони ж — сервісні). 
Настав час поговорити про останні.

![Сервісні повідомлення](../images/ru/messages/service_messages.png)

Незважаючи на те, що вони виглядають незвично і взаємодія з ними обмежена, це все ще 
повідомлення, у яких є свої айдишники та навіть власник. Варто зазначити, що спектр застосування 
сервісних повідомлень з роками змінювався і сейчас, швидше за все, ваш бот з ними працювати не буде, 
або тільки видаляти.

Не будемо сильно заглиблюватись у деталі та розглянемо один конкретний приклад: відправка 
привітального повідомлення учаснику, що вступив. У такого служебного повідомлення буде content_type 
рівний "new_chat_members", але взагалі це об'єкт Message, у якого заповнено однойменне поле. 

```python
@dp.message(F.new_chat_members)
async def somebody_added(message: Message):
    for user in message.new_chat_members:
        # властивість full_name бере відразу ім'я І прізвище 
        # (на скриншоті вище у юзерів немає прізвища)
        await message.reply(f"Привіт, {user.full_name}")
```

![Додано кілька юзерів](../images/ru/messages/multiple_add.png)

Важливо пам'ятати, що `message.new_chat_members` є списком, тому що один користувач може 
додати відразу кількох учасників. Також не надо плутати поля `message.from_user` та 
`message.new_chat_members`. Перше — це суб'єкт, тобто той, хто вчинив дію. Друге — 
це об'єкти дії. Тобто якщо ви бачите повідомлення виду «Анна додала Бориса та Віктора», то 
`message.from_user` — це інформація про Анну, а список `message.new_chat_members` містить 
інформацію про Бориса з Віктором.

!!! warning "Не варто цілком покладатися на сервісні повідомлення!"
    У служебних повідомленнях про додавання (new_chat_members) та вихід (left_chat_member) є
    одна неприємна особливість: вони ненадійні, тобто вони можуть не створюватися взагалі.  
    Наприклад, повідомлення про new_chat_members перестає створюватися при ~10k учасниках у групі, 
    а left_chat_member вже при 50 (але при написанні цієї глави я зіткнувся з тим, що в одній 
    з груп left_chat_member не з'явився і при 9 учасниках. А через півгодини там же з'явився 
    при виході іншої людини).

    З виходом Bot API 5.0 у розробників з'явився куди надійніший спосіб бачити входи/виходи 
    учасників у групах будь-якого розміру, **а також у каналах**. Але про це поговоримо 
    [іншим разом](special-updates.md).

## Бонус: приховуємо посилання в тексті {: id="bonus" }

Трапляються ситуації, коли хочеться відправити довге повідомлення з картинкою, але ліміт на підписи до медіафайлів становить 
всього 1024 символи проти 4096 у звичайному текстовому, а вставляти внизу посилання на медіа — виглядає деякрасиво.  
Для вирішення цієї проблеми ще багато років тому придумали підхід зі «прихованими посиланнями» в HTML-розітці. Суть у тому, що 
можна помістити посилання в [пробіл нульової ширини](http://www.fileformat.info/info/unicode/char/200b/index.htm) і вставити 
всю цю конструкцію на початок повідомлення. Для спостерігача у повідомленні немає нічого лишнього, а сервер Telegram все бачить і чесно 
додає попередній перегляд.  
Розробники aiogram для цього навіть зробили спеціальний допоміжний метод `hide_link()`:
```python
# новий імпорт!
from aiogram.utils.markdown import hide_link

@dp.message(Command("hidden_link"))
async def cmd_hidden_link(message: Message):
    await message.answer(
        f"{hide_link('https://telegra.ph/file/562a512448876923e28c3.png')}"
        f"Документація Telegram: *існує*\n"
        f"Користувачі: *не читають документацію*\n"
        f"Груша:"
    )
```

![Зображення з прихованим посиланням](../images/ru/messages/hidden_link.png)

А за допомогою LinkPreviewOptions (див. вище) можна зробити медіафайл сверху з довгою підписом в 4096 символів нижче.

На цьому все. До наступних глав!  
<s><small>Ставте лайки, підписуйтесь, тисніть дзвіночок</small></s>

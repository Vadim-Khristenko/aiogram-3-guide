---
title: Розширені повідомлення
description: Розширені повідомлення
---

# Розширені повідомлення

!!! info ""
    Використовувана версія aiogram: 3.29.0

Багато років у Telegram існувало лише три способи форматування повідомлень: **plaintext**, тобто без форматування,
**HTML** та **Markdown** у двох варіантах, один із яких визнано застарілим. Коли планету охопив бум нейромереж, можливості 
прикрашання тексту в месенджері почали виглядати доволі скромно. ChatGPT генерує красиві таблиці, формули 
і списки зі сносками, а відобразити все це в Telegram без костилів неможливо. Розробники Bot API в оновленні 
Bot API 10.1 (червень 2026 р.) додали функцію під назвою Rich Messages, покликану вирішити цю проблему. 
У цій главі поговоримо про ці повідомлення, наскільки вони «розширені».

## Загальна інформація {: id="intro" }

Що ж таке «багаті повідомлення» (звучить крінжово, тож далі я буду називати їх англійською Rich Messages або RM)? 
Документація описує їх так:

 > Rich Messages призначені для сильно структурованих відповідей: звітів, відповідей від ШІ, 
> документації, технічних статей та іншого подібного складного контенту.
> Такі повідомлення підтримують як Rich Markdown, так і Rich HTML. 
> Rich Markdown використовує GitHub Flavored Markdown і може включати підтримувані 
> HTML-теги прямо в тому самому повідомленні. Rich HTML дає ботам більш точний контроль над ще більшою кількістю 
> можливостей форматування за допомогою спеціальних тегів.

 > Підтримувані стилі включають:  
> - Заголовки, абзаци, роздільники, списки та todo-списки.  
> - Вкладене inline-форматування, включно з жирним шрифтом, курсивом, підкресленням, закресленням, спойлером, кодом, нижнім і верхнім регістром.  
> - Таблиці з вирівнюванням, підписами, рамками, «смугастим» стилем, об'єднанням колонок та об'єднанням рядків.  
> - Медіаблоки для фотографій, відео та аудіофайлів, з підписами та вказанням авторства.  
> - Блокові цитати, виділені цитати, згортальні блоки details, якорі та посилання всередині документа.  
> - Примітки та текст, на який можна посилатися.  
> - Повна підтримка LaTeX, включно як inline-формул, так і блочних формул.  
> - Карти з координатами, колажі, слайдшоу та багато іншого.  

 > **Обмеження Rich Messages**. На Rich Messages діють такі обмеження:  
> - До **32768** UTF-8 символів у тексті розширеного повідомлення, включаючи альтернативний текст кастомних емодзі та вихідний код формули.  
> - До **500** блоків, включно з вкладеними блоками, елементами списків, елементами нумерованих списків, рядками таблиць, блоками цитат та блоками `details`.  
> - До **16** рівнів вкладеного форматування та блоків.  
> - До **50** медіа-вкладень загалом, включно з фотографіями, відео та аудіофайлами.  
> - До **20** колонок у таблиці.  

Виглядають RM справді круто. Якщо ще не бачили їх у дії, можете подивитися гарну демонстрацію в 
[документації](https://core.telegram.org/bots/features#advanced-formatting-options) або в 
офіційному демонстраційному боті [@richtextdemobot](https://telegram.dog/richtextdemobot).

## Відмінність від звичайних повідомлень {: id="rich-vs-regular" }

Rich Messages **не замінюють** старий добрий `sendMessage` з MarkdownV2 і HTML. 
Це два різні інструменти для різних завдань:

* **Звичайні повідомлення** (`sendMessage`) — це легкий формат для коротких текстів: підтверджень введення, реплік у діалозі, 
  пари рядків з жирним словом і посиланням. Тут також лишаються «ексклюзивні» можливості, як-от часткове цитування
  і пересилання цитати в інший чат.

* **Rich Messages** (`sendRichMessage`) — вдалий варіант, коли потрібно надіслати «складний» текст: звіт, документацію,
  довгу відповідь від нейромережі. Заголовки, таблиці, сноски, формули, згортальні блоки — усе те, заради чого раніше
  доводилося рендерити відповідь картинкою через PIL або робити ASCII-арт. Такі повідомлення за потреби можна
  й відредагувати — [нижче](#editing) подивимося, як саме.

Іншими словами: якщо вам потрібно надіслати просте і коротке «Готово ✅» — це `sendMessage`. 
Якщо вам потрібно надіслати структурований звіт з таблицями і сносками на половину екрана — це `sendRichMessage`.

Ще один важливий момент, який варто згадати перед переходом до практичної частини:
у RM не існує такого поняття, як "parse mode": мова розмітки залежить від того, який саме аргумент
функції ви оберете — `markdown` або `html`. Краще явно, ніж неявно.

## Як відправити Rich Message {: id="how-to-send" }

У Bot API за відправлення відповідає метод [sendRichMessage](https://core.telegram.org/bots/api#sendrichmessage),
а сам контент описується об'єктом [InputRichMessage](https://core.telegram.org/bots/api#inputrichmessage).

Приклад підготовки тексту в двох різних мовах розмітки:

```python
from aiogram.types import InputRichMessage

# Варіант з Markdown
md_content = InputRichMessage(markdown="# Заголовок\n\nПривіт, **світ**!")

# Варіант з HTML — те саме, але іншим синтаксисом
html_content = InputRichMessage(html="<h1>Заголовок</h1><p>Привіт, <b>світ</b>!</p>")
```

Далі цей об'єкт можна відправити або напряму через `bot.send_rich_message(...)`, або через звичні шорткати
у `Message`: `answer_rich()` і `reply_rich()`

Зберемо осмислений приклад, в якому задіяні заголовки різних рівнів, таблиця, формула та сноска. Цього разу
опишемо повідомлення через **Rich HTML** — для цього достатньо покласти текст у поле `html`. Текст опишемо
окремою константою:

```python title="bot/handlers/rich_send.py"
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InputRichMessage, Message

router = Router(name="rich_send")

REPORT_HTML = """\
<h1>Звіт за квартал</h1>
<p>Невеликий приклад того, як <b>Rich Messages</b> зберігають структуру: тут є \
заголовки різного рівня, таблиця, формула і примітка<sup><a name="ref-1"></a><a href="#note-1">1</a></sup>.</p>
<h2>Ключові метрики</h2>
<table>
<tr><th align="left">Метрика</th><th align="right">Було</th><th align="right">Стало</th></tr>
<tr><td align="left">MRR</td><td align="right">$35k</td><td align="right">$42k</td></tr>
<tr><td align="left">Активні чати</td><td align="right">1 240</td><td align="right">1 510</td></tr>
<tr><td align="left">Відключені боти</td><td align="right">12</td><td align="right">7</td></tr>
</table>
<h2>Трохи математики</h2>
<p>Приріст рахуємо за простою формулою:</p>
<tg-math-block>rate = (new - old) / old</tg-math-block>
<blockquote>Це блочна цитата. У ній можна містити <i>курсив</i>, \
<code>код</code> і навіть <tg-spoiler>спойлер</tg-spoiler>.</blockquote>

<footer><a name="note-1"></a><a href="#ref-1">1.</a>Цифри вигадані для прикладу і нічого не відображають. ↩️</footer>
"""


@router.message(Command("sendrich"))
async def cmd_send_rich(
        message: Message,
) -> None:
    await message.answer_rich(
        rich_message=InputRichMessage(html=REPORT_HTML),
    )
```

Що тут відбувається:

* Заголовки задаються звичними тегами `<h1>`…`<h6>`, абзаци — тегом `<p>`. 
* Примітка — справжня інтерактивна, працює в обох напрямках на якорях. 
У тексті маркер це `<sup>`, всередині якого якір `<a name="ref-1">` (точка повернення) і посилання 
`<a href="#note-1">1</a>` на текст примітки. У футері (пункт 5) все дзеркально. 
Тег `<a>` з атрибутом name задає якір, а `<a href="#имя">` — посилання на нього всередині повідомлення 
(з пустим `<a href="#">` посилання веде на початок).
* Таблиця — це тег `<table>` зі рядками `<tr>` і комірками `<td>`/`<th>` (заголовочні). 
Вирівнювання задається атрибутом `align` (`left`/`center`/`right`), а для вертикального є `valign`. 
Підтримуються також `colspan`/`rowspan`, рамки та «смугастий» стиль.
* Блочна формула — кастомний тег `<tg-math-block>`, всередині звичайний LaTeX. Telegram відрендерить формулу сам.
* Футер `<footer>` — тут живе текст примітки і зворотнє посилання ↩️ до маркера: якір `<a name="note-1">` 
дозволяє «перейти» вниз до примітки, а посилання `<a href="#ref-1">` повертає нагору. 
* Всередині `<blockquote>`, видно, що inline-теги (`<i>`, `<code>`, `<tg-spoiler>`) працюють і у вкладених блоках.
* Шорткат `answer_rich()` відправляє `InputRichMessage` у той самий чат. 
Оскільки ми заповнили поле `html`, Telegram трактує текст як Rich HTML.

Результат виглядає так: 

![Розширене повідомлення](images/rich-messages/uk/sendrich_dark.png#only-dark){ width="460" }
![Розширене повідомлення](images/rich-messages/uk/sendrich_light.png#only-light){ width="460" }

!!! warning "Не забувайте екранувати"
    Як і в звичайному HTML-форматуванні, символи `<`, `>` і `&`, які не є частиною тега, потрібно замінювати на
    `&lt;`, `&gt;` і `&amp;`. Інакше Telegram спробує прийняти частину тексту за тег і зламає розмітку.

!!! tip "Markdown і HTML можна поєднувати"
    Rich Markdown дозволяє вставляти підтримувані HTML-теги прямо всередину markdown-тексту. Це зручно, коли якийсь
    блок простіше виразити тегом, а основний текст хочеться тримати в markdown. А якщо потрібен повний контроль над усіма
    можливостями форматування — беріть цілком `html`-варіант, як ми зробили вище.

## Редагування Rich Messages {: id="editing" }

Навчилися відправляти, тепер про редагування. Окремого методу на кшталт `editRichMessage` у Bot API не додали:
натомість у [editMessageText](https://core.telegram.org/bots/api#editmessagetext) з'явився
аргумент `rich_message`. Аргументи `text` і `rich_message` взаємовиключні: потрібно передати рівно один з них.
У aiogram, відповідно, працює звичний шорткат `edit_text()`.

Зберемо маленький приклад: на команду `/sendrichedit` бот відправляє чек-лист релізу (todo-список — якраз одна з
«фішок» RM) з інлайн-кнопкою, а при натисканні на кнопку позначає всі пункти виконаними:

```python title="bot/handlers/rich_edit.py"
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputRichMessage,
    Message,
)

router = Router(name="rich_edit")

CHECKLIST_BEFORE = """\
# Чек-лист релізу

Прогрес: **0 із 3**

- [ ] Прогнати тести
- [ ] Оновити документацію
- [ ] Задеплоїти бота
"""

CHECKLIST_AFTER = """\
# Чек-лист релізу

Прогрес: **3 із 3** 🎉

- [x] Прогнати тести
- [x] Оновити документацію
- [x] Задеплоїти бота
"""


@router.message(Command("sendrichedit"))
async def cmd_send_rich_edit(
        message: Message,
) -> None:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Виконати всі пункти",
            callback_data="complete_checklist",
        )
    ]])
    await message.answer_rich(                                    # [1]
        rich_message=InputRichMessage(markdown=CHECKLIST_BEFORE),
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "complete_checklist")
async def on_complete_checklist(
        callback: CallbackQuery,
) -> None:
    await callback.message.edit_text(                             # [2]
        rich_message=InputRichMessage(markdown=CHECKLIST_AFTER),  # [3]
    )
    await callback.answer()
```

Покроково:

1. Шорткат `answer_rich()` приймає `reply_markup` точно так само, як звичайний `answer()`: до розширеного повідомлення можна
   прикрутити будь-яку інлайн-клавіатуру.
2. Редагування — через знайомий, як у звичайних повідомленнях, `edit_text()`. А оскільки ми не передали `reply_markup`,
   після редагування кнопка зникне — усі пункти виконано, натискати більше нічого.
3. Замість аргумента `text` передаємо `rich_message` з новим вмістом — звичайний `InputRichMessage`, 
   точно такий самий, як при відправленні.

![Розширене повідомлення](images/rich-messages/sendrichedit_dark.png#only-dark){ width="500" }
![Розширене повідомлення](images/rich-messages/sendrichedit_light.png#only-light){ width="500" }

## Стрімінг через `sendRichMessageDraft` {: id="streaming" }

Поговоримо про стрімінг тексту. В одному з минулих оновлень додали `sendMessageDraft` для звичайних повідомлень, 
аналогічний метод існує і для розширених повідомлень. Взагалі, про стрімінг уже було достатньо докладно написано 
[в окремій замітці](../blog/posts/project_threads_llm.md#_3), але варто повторити загальні принципи ще раз.

Стрімінг працює так:

* Метод показує користувачу **чернетку** — тимчасовий попередній перегляд повідомлення. Ця чернетка ефемерна: вона живе близько
  30 секунд і сама зникає, в історії чату не залишається.
* У чернетки є `draft_id` — ненульовий ідентифікатор. Усі оновлення з одним і тим самим `draft_id` Telegram анімує
  як плавну зміну тієї самої чернетки, без мерехтіння.
* Коли генерація завершена, чернетку потрібно «зафіксувати»: відправити готове повідомлення звичайним `sendRichMessage`.

```python title="bot/handlers/rich_stream.py"
import asyncio
from random import randint

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import InputRichMessage, Message

router = Router(name="rich_stream")

# Остаточний текст, який ми будемо друкувати шматками.
FINAL_MARKDOWN = """\
# Що таке стрімінг чернетки

Метод `sendRichMessageDraft` показує користувачу **тимчасове прев'ю**
повідомлення, поки воно ще генерується — точно так само поводяться нейромережні
асистенти, які поступово друкують відповідь.

## Як це працює

- Чернетка **ефемерна**: вона живе близько 30 секунд і сама зникає.
- Всі оновлення з одним і тим же `draft_id` Telegram анімує як плавну правку.
- Щоб повідомлення лишилося в чаті назавжди, наприкінці потрібно відправити його
  звичайним `sendRichMessage`.
"""


def _build_chunks(text: str) -> list[str]:                        # [1]
    words = text.split(" ")
    chunks: list[str] = []
    step = 12
    for i in range(step, len(words), step):
        chunks.append(" ".join(words[:i]))
    chunks.append(text)
    return chunks

@router.message(Command("sendrichstream"))
async def cmd_send_rich_stream(
        message: Message,
        bot: Bot,
) -> None:
    # Генеруємо випадковий id чернетки
    draft_id = randint(1, 100_000_000)                            # [2]

    # Імітуємо початкову затримку перед «першим токеном»:
    # покажемо заглушку для порожнього тексту і почекаємо паузу в 2 секунди.
    await bot.send_rich_message_draft(                            # [3]
        chat_id=message.chat.id,
        draft_id=draft_id,
        rich_message=InputRichMessage(
            markdown="<tg-thinking>Думаю...</tg-thinking>"        # [4]
        ),
    )
    await asyncio.sleep(2.0)

    for chunk in _build_chunks(FINAL_MARKDOWN):
        await bot.send_rich_message_draft(
            chat_id=message.chat.id,
            draft_id=draft_id,
            rich_message=InputRichMessage(markdown=chunk),
        )
        await asyncio.sleep(0.7)                                  # [5]
    await message.answer_rich(                                    # [6]
        rich_message=InputRichMessage(markdown=FINAL_MARKDOWN),
    )
```

Пункт за пунктом:

1. В навчальних цілях ми ріжемо підсумковий текст на зростаючі префікси. У реальному боті на їхньому місці були б токени 
від LLM, які ви накопичуєте в буфер і періодично відправляєте як чернетку.
2. `draft_id` має бути ненульовим. Використаємо випадкове число як такий ідентифікатор.
3. Безпосередньо відправлення чергової частини. Зауважте, що метод повертає `True`/`False`, \
а не об'єкт `Message` — це ж не справжнє повідомлення, а прев'ю.
4. Заглушка, яку можна показувати, поки взагалі немає тексту. Красиво анімовано, до речі.
5. Невелика пауза між оновленнями, щоб не вийти на ліміти флуду. Підбирайте інтервал під своє навантаження.
6. Фінал: відправляємо повний текст звичайним `answer_rich()`. Це повідомлення вже залишиться в чаті.

!!! note "Не намагайтеся стрімити посимвольно"
    Кожен виклик `send_rich_message_draft` — це мережевий запит. Накопичіть розумний буфер (кілька слів або один рядок)
    і надсилайте попередній перегляд раз на кілька сотень мілісекунд, інакше Telegram швидко накладе на вас обмеження.

Як це виглядає «у дії» на відео:

![тип:відео](images/rich-messages/streaming_dark.mp4)

## Медіафайли {: id="media" }

Не тільки текст — у RM можна вбудовувати медіа. Тут виникає неприємна особливість \nRich Messages: медіафайли не можна передавати через `file_id`, лише за HTTP(S)-посиланнями. 

У Rich Markdown для медіафайлів підтримується стандартний Markdown-синтаксис: `![alt-текст](URL "title")`. Однак \nчастина з alt-текстом (в звичайному вебі він використовується в разі, коли медіафайл не завантажився або в режимі «тільки текст») \nу Telegram ніде не відображається, а видимий підпис потрібно задавати одразу після URL у лапках. \nВтім, подивіться приклад нижче — і все стане зрозуміло:

```python title="bot/handlers/rich_media.py"
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InputRichMessage, Message

router = Router(name="rich_media")

GALLERY_MARKDOWN = """\
# Галерея HTTP-котиків

Кілька зображень у межах одного багатого повідомлення, у кожного — опис і підпис.

**204 No Content** — сервер успішно опрацював запит, але повертати в тілі відповіді нічого. Клієнт залишається на поточній сторінці і при необхідності оновлює дані за заголовками відповіді.

![](https://http.cat/images/204.jpg "HTTP 204 No Content")

**301 Moved Permanently** — запитуваний ресурс остаточно перемістився на нову адресу зі заголовка `Location`. Усі наступні запити й закладки варто направляти вже туди, а пошукові системи з часом оновлять посилання.

![](https://http.cat/images/301.jpg "HTTP 301 Moved Permanently")

**418 I'm a teapot** — жартівливий код з першоквітневого RFC 2324: сервер-чайник категорично відмовляється заварювати каву. У реальних API не використовується, але живе як улюблена пасхалка.

![](https://http.cat/images/418.jpg "HTTP 418 I am a Teapot")

Під галереєю можна спокійно продовжувати текст: заголовки, списки і все інше
працюють як зазвичай.
"""


@router.message(Command("sendrichmedia"))
async def cmd_send_rich_media(
        message: Message,
) -> None:
    await message.answer_rich(
        rich_message=InputRichMessage(markdown=GALLERY_MARKDOWN),
    )
```

Верхня частина готового повідомлення на скріншоті:

![Розширене повідомлення](images/rich-messages/sendrichmedia_dark.png#only-dark){ width="500" } 
![Розширене повідомлення](images/rich-messages/sendrichmedia_light.png#only-light){ width="500" } 

!!! note "Колаж, слайд-шоу та інші медіа"
    Кілька зображень підряд — це базовий випадок. Для тонкого керування компонуванням у Rich HTML є окремі
    теги: `<photo>`, `<video>` і `<audio>` для одиночних медіа, а також кастомні `<tg-collage>` (колаж) і
    `<tg-slideshow>` (слайд-шоу), всередину яких вкладаються медіа-блоки. Переглянути рендеринг у живому режимі можна в
    [@richtextdemobot](https://telegram.dog/richtextdemobot).


## Як перехопити та розібрати Rich Message {: id="parsing" }

Окрім відправки Rich Messages, потрібно навчитися їх приймати та «розуміти». Тим паче, що одними з перших, 
хто опанував новий тип повідомлень, стали спамери. У класі [Message](https://core.telegram.org/bots/api#message)
з'явилося нове поле `rich_message` типу [RichMessage](https://core.telegram.org/bots/api#richmessage). Воно заповнюється,
коли боту надходить RM.

Влаштований `RichMessage` просто: це список блоків (`blocks`). Кожен блок має спільне поле `type` (`heading`, `paragraph`,
`table`, `list`, `photo`, `slideshow`, `collage`, `footer` тощо), а текстові блоки несуть у поле `text` дерево об'єктів
`RichText`. Це дерево може бути рядком, списком вузлів або стилізованим вузлом (жирний, курсив...), всередині якого знову
лежить `RichText`. Щоб витягти з нього «чистий» текст, зручно написати маленьку рекурсивну функцію:

```python title="bot/handlers/rich_parse.py"
from collections import Counter

from aiogram import F, Router
from aiogram.types import Message

router = Router(name="rich_parse")


def flatten_text(node) -> str:
    if node is None:
        return ""
    if isinstance(node, str):                                     # [1]
        return node
    if isinstance(node, list):                                    # [2]
        return "".join(flatten_text(item) for item in node)
    # У кастомних емодзі немає вкладеного text, натомість є альтернативний текст
    if getattr(node, "type", None) == "custom_emoji":             # [3]
        return node.alternative_text
    return flatten_text(getattr(node, "text", None))              # [4]


@router.message(F.rich_message)                                   # [5]
async def on_rich_message(
        message: Message,
) -> None:
    blocks = message.rich_message.blocks

    stats = "\n".join(f"• {block.type}" for block in blocks)      # [6]

    headings = [                                                  # [7]
        flatten_text(block.text)
        for block in blocks
        if block.type == "heading"
    ]

    table = next((b for b in blocks if b.type == "table"), None)  # [8]

    lines = [
        f"Rich Message з {len(blocks)} блоків.",
        f"Склад: {stats}",
    ]
    if headings:
        toc = "\n".join(f"• {title}" for title in headings)
        lines.append(f"\nЗаголовки:\n{toc}")
    if table is not None:
        first_row = " | ".join(flatten_text(cell.text) for cell in table.cells[0])
        lines.append(f"\nПерший рядок таблиці: {first_row}")

    await message.answer("\n".join(lines))
```

Розберемо ключові місця:

1. Базовий випадок рекурсії: якщо вузол — звичайний рядок, повертаємо його як є.
2. Якщо вузол — список, з'єднуємо результати обходу кожного елемента.
3. У кастомного емодзі немає вкладеного `text`, натомість є `alternative_text` — беремо його.
4. У всіх інших випадках це стилізований вузол: спускаємося в його поле `text` ще на рівень глибше.
5. Магічний фільтр `F.rich_message` спрацьовує лише якщо у вхідного повідомлення заповнене поле `rich_message`. 
   Так ми ловимо саме багаті повідомлення і не заважаємо командам.
6. Збираємо блоки в порядку їх появи.
7. Збираємо всі заголовки в зміст. Одночасно видно, як `flatten_text` витягує текст із заголовка, 
   навіть якщо він обгорнутий у курсив або жирний.
8. Якщо всередині є таблиця, дістаємо її перший рядок. Комірки лежать в `table.cells` як список списків (`строки → ячейки`), 
   а текст комірки — знову дерево RichText.

Якщо переслати боту його власний приклад із HTTP-котиками, то ви повинні побачити таке повідомлення:

```
Rich Message із 9 блоків.
Склад:
• heading
• paragraph
• paragraph
• photo
• paragraph
• photo
• paragraph
• photo
• paragraph

Заголовки:
• Галерея HTTP-котиків
```


## Висновок {: id="conclusion" }

Rich Messages — це давно назрілий відповідь Telegram на епоху нейромереж і повсюдного використання Markdown.
У цій главі ми навчилися надсилати такі повідомлення (через `markdown`/`html`), редагувати їх, розбирати вхідні 
по блоках і стримити відповіді через ефемерні чернетки. За кадром залишилося ще багато блоків — карти, згортані `details`,
аудіо та відео, блочні формули — але принцип скрізь один і той самий, тож, озброївшись основами, решту ви опануєте
за [документацією](https://core.telegram.org/bots/api#inputrichmessage) та [демо-ботом](https://telegram.dog/richtextdemobot).
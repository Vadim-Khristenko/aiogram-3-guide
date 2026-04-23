---
title: Знайомство з aiogram
description: Знайомство з aiogram
---

# Знайомство з aiogram {: id="quickstart" }

!!! info ""
    Використовувана версія aiogram: 3.27.0  
    Перевірено на версії aiogram: 3.27.0 | 23.04.2026

!!! warning "Деякі деталі свідомо спрощені!"
    Автор цієї книги переконаний, що окрім теорії повинна бути і практика. Щоб максимально спростити повторення 
    наведеного далі коду, довелося використовувати підходи, придатні лише для локальної розробки 
    та навчання.

    Так, наприклад, у всіх або майже у всіх розділах токен бота буде вказуватися прямо у вихідних текстах. 
    Це **поганий** підхід, оскільки може призвести до розкриття токена, якщо ви забудете його видалити перед завантаженням 
    коду у публічний репозиторій (наприклад, GitHub).

    Або іноді як сховища даних будуть використовуватися структури, розташовані виключно в 
    оперативній пам'яті (словники, списки...). Насправді такі об'єкти небажані, оскільки зупинка 
    бота призведе до безповоротної втрати даних.

    Також механізмом отримання оновлень від Telegram обрано поллінг, оскільки він гарантовано працює 
    у переважній більшості середовищ і підходить практично всім розробникам. 

    **Важливо пам'ятати, що автор ставить перед собою мету пояснити саме роботу з Telegram Bot API за допомогою 
    aiogram, а не взагалі весь Computer Science у всьому його різноманітті.**

## Термінологія {: id="glossary" }

Щоб говорити в одних і тих же поняттях, введемо деякі терміни, аби надалі не плутатися:

* ПП — приватні повідомлення, у контексті бота це діалог один на один з користувачем, а не група/канал.
* Чат — загальна назва для ПП, груп, супергруп і каналів.
* Оновлення — будь-яка подія з [цього списку](https://core.telegram.org/bots/api#update): 
повідомлення, редагування повідомлення, колбек, інлайн-запит, платіж, додавання бота в групу тощо. 
* Хендлер — асинхронна функція, яка отримує від диспетчера/роутера чергове оновлення 
і обробляє його.
* Диспетчер — об'єкт, що займається отриманням оновлень від Telegram з подальшим вибором хендлера 
для обробки отриманого оновлення.
* Роутер — аналогічно диспетчеру, але відповідає за підмножину множини хендлерів. 
**Можна сказати, що диспетчер — це кореневий роутер**.
* Фільтр — вираз, який зазвичай повертає True або False і впливає на те, чи буде викликаний хендлер.
* Мідлвеар — прошарок, який втручається в обробку оновлень. 

## Встановлення {: id="installation" }

Для початку давайте створимо каталог для бота, організуємо там virtual environment (далі venv) і
встановимо бібліотеку [aiogram](https://github.com/aiogram/aiogram).  
Перевіримо, що встановлено Python версії 3.11 або вище (якщо ви знаєте, що встановлено 3.11 і вище, можете пропустити цей розділ):

!!! warning "Важливо про версії Python"
    Починаючи з aiogram 3.14+, мінімальна підтримувана версія Python — **3.9**. 
    Python 3.9 досягає End of Life (EOL) і незабаром не буде підтримуватися Aiogram. 
    Рекомендується використовувати Python **3.12** або новіший для кращої продуктивності та безпеки.

```plain
[groosha@main lesson_01]$ python3.12
Python 3.12.11 (main, July 06 2025, 16:35:07) 
[GCC 11.1.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> exit()
[groosha@main lesson_01]$ 
```

Тепер створимо файл `requirements.txt`, у якому вкажемо використовувану нами версію aiogram. Також нам знадобиться 
бібліотека pydantic-settings для файлів конфігурації.
!!! important "Про версії aiogram"
    У цьому розділі використовується aiogram **3.x**, перед початком роботи рекомендую заглянути до 
    [каналу релізів](https://t.me/aiogram_live) бібліотеки і перевірити наявність більш нової версії. Підійде будь-яка 
    більш нова, що починається з цифри 3, оскільки aiogram 2.x більше не розглядатиметься і вважається застарілим.

```plain
[groosha@main 01_quickstart]$ python3.12 -m venv venv
[groosha@main 01_quickstart]$ echo "aiogram<4.0" > requirements.txt
[groosha@main 01_quickstart]$ echo "pydantic-settings" >> requirements.txt
[groosha@main 01_quickstart]$ source venv/bin/activate
(venv) [groosha@main 01_quickstart]$ pip install -r requirements.txt 
# ...тут купа рядків про встановлення...
Successfully installed ...тут довгий список...
[groosha@main 01_quickstart]$
```

Зверніть увагу на префікс "venv" у терміналі. Він вказує, що ми знаходимося у віртуальному середовищі з іменем "venv".
Перевіримо, що всередині venv виклик команди `python` вказує на все той же Python 3.12:  
```plain
(venv) [groosha@main 01_quickstart]$ python
Python 3.12.11 (main, July 06 2025, 16:35:07) 
[GCC 11.1.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> exit()
(venv) [groosha@main 01_quickstart]$ deactivate 
[groosha@main 01_quickstart]$ 
```

Останньою командою `deactivate` ми вийшли з venv, щоб він нам не заважав. 

!!! info ""
    Якщо для написання ботів ви використовуєте PyCharm, рекомендую також встановити сторонній плагін 
    [Pydantic](https://plugins.jetbrains.com/plugin/12861-pydantic) для підтримки автодоповнення коду 
    у телеграмних об'єктах.

## Перший бот {: id="hello-world" }

Давайте створимо файл `bot.py` з базовим шаблоном бота на aiogram:
```python title="bot.py"
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

# Включаємо логування, щоб не пропустити важливі повідомлення
logging.basicConfig(level=logging.INFO)
# Об'єкт бота
bot = Bot(token="0000000000:AaBbCcDdEeFfGgHhIiJjKkLlMmNn")
# Диспетчер
dp = Dispatcher()

# Хендлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привіт!")

# Запуск процесу поллінгу нових оновлень
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```

Перше, на що потрібно звернути увагу: aiogram — асинхронна бібліотека, тому ваші хендлери також повинні бути асинхронними, 
а перед викликами методів API потрібно ставити ключове слово **await**, тому що ці виклики повертають [корутини](https://docs.python.org/3/library/asyncio-task.html#coroutines).

!!! info "Асинхронне програмування в Python"
    Не варто нехтувати офіційною документацією!  
    Прекрасний туторіал з asyncio доступний [на сайті Python](https://docs.python.org/3/library/asyncio-task.html).

Якщо ви в минулому працювали з якоюсь іншою бібліотекою для Telegram, наприклад, pyTelegramBotAPI, то концепція
хендлерів (обробників подій) вам одразу стане зрозумілою, різниця лише в тому, що в aiogram хендлерами керує диспетчер.  
Диспетчер реєструє функції-обробники, додатково обмежуючи перелік викликаючих їх подій через фільтри. 
Після отримання чергового оновлення (події від Telegram), диспетчер вибере потрібну функцію обробки, підходящу за всіма 
фільтрами, наприклад, «обробка повідомлень, що є зображеннями, у чаті з ID ікс і з довжиною підпису ігрек». Якщо дві 
функції мають однакові за логікою фільтри, то буде викликана та, що зареєстрована раніше.

Щоб зареєструвати функцію як обробник повідомлень, потрібно зробити одну з двох дій:  
1. Навісити на неї [декоратор](https://devpractice.ru/python-lesson-19-decorators/), як у прикладі вище. 
З різними типами декораторів ми познайомимося пізніше.  
2. Напряму викликати метод реєстрації у диспетчера або роутера.

Розглянемо наступний код: 
```python
# Хендлер на команду /test1
@dp.message(Command("test1"))
async def cmd_test1(message: types.Message):
    await message.reply("Тест 1")

# Хендлер на команду /test2
async def cmd_test2(message: types.Message):
    await message.reply("Тест 2")
```

Давайте запустимо з ним бота:  
![Команда /test2 не працює](../images/uk/quickstart/l01_1_Light.jpg#only-light)
![Команда /test2 не працює](../images/uk/quickstart/l01_1_Dark.jpg#only-dark)

Хендлер `cmd_test2` не спрацює, тому що диспетчер про нього не знає. Виправимо цю помилку 
і окремо зареєструємо функцію:
```python
# Хендлер на команду /test2
async def cmd_test2(message: types.Message):
    await message.reply("Тест 2")

# Десь в іншому місці, наприклад, у функції main():
dp.message.register(cmd_test2, Command("test2"))
```

Знову запустимо бота:  
![Обидві команди працюють](../images/uk/quickstart/l01_2_Light.jpg#only-light)
![Обидві команди працюють](../images/uk/quickstart/l01_2_Dark.jpg#only-dark)

## Синтаксичний цукор {: id="sugar" }

Для того щоб зробити код чистішим і читабельнішим, aiogram розширює можливості стандартних об'єктів Telegram.
Наприклад, замість `bot.send_message(...)` можна написати `message.answer(...)` або `message.reply(...)`. У останніх
двох випадках не потрібно підставляти `chat_id`, мається на увазі, що він такий же, як і у вихідному повідомленні.  
Різниця між `answer` і `reply` проста: перший метод просто відправляє повідомлення у той же чат, другий робить "відповідь" на 
повідомлення з `message`:
```python
@dp.message(Command("answer"))
async def cmd_answer(message: types.Message):
    await message.answer("Це проста відповідь")


@dp.message(Command("reply"))
async def cmd_reply(message: types.Message):
    await message.reply('Це відповідь з "відповіддю"')
```
![Різниця між message.answer() і message.reply()](../images/uk/quickstart/l01_3_Light.jpg#only-light)
![Різниця між message.answer() і message.reply()](../images/uk/quickstart/l01_3_Dark.jpg#only-dark)

Більше того, для більшості типів повідомлень є допоміжні методи виду 
"answer_{type}" або "reply_{type}", наприклад:
```python
@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji="🎲")
```

!!! info "що означає 'message: types.Message' ?"
    Python є інтерпретованою мовою з [сильною, але динамічною типізацією](https://uk.wikipedia.org/wiki/%D0%A1%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%B0_%D1%82%D0%B8%D0%BF%D1%96%D0%B7%D0%B0%D1%86%D1%96%D1%97),
    тому вбудована перевірка типів, як, наприклад, у C++ або Java, відсутня. Однак починаючи з версії 3.5 
    у мові з'явилася підтримка [підказок типів](https://docs.python.org/3/library/typing.html), завдяки яким
    різні чекери та IDE на кшталт PyCharm аналізують типи використовуваних значень і підказують
    програмісту, якщо він передає щось не те. У даному випадку підказка `types.Message` повідомляє
    PyCharm-у, що змінна `message` має тип `Message`, описаний у модулі `types` бібліотеки
    aiogram (див. імпорти на початку коду). Завдяки цьому IDE може на льоту підказувати атрибути і функції.

При виклику команди `/dice` бот відправить у той же чат ігральний кубик. Звичайно, якщо його треба відправити у якийсь
інший чат, то доведеться по-старому викликати `await bot.send_dice(...)`. Але об'єкт `bot` (екземпляр класу Bot) може бути 
недоступним у області видимості конкретної функції. В aiogram 3.x об'єкт бота, якому прийшло оновлення, неявно 
прокидається у хендлер і його можна дістати як аргумент `bot`. Припустимо, ви хочете по команді `/dice` 
відправляти кубик не у той же чат, а у канал з ID -100123456789. Перепишемо попередню функцію:

```python
# не забудьте про імпорт
from aiogram.enums.dice_emoji import DiceEmoji

@dp.message(Command("dice"))
async def cmd_dice(message: types.Message, bot: Bot):
    await bot.send_dice(-100123456789, emoji=DiceEmoji.DICE)
```

## Передача додаткових параметрів {: id="pass-extras" }

Іноді при запуску бота може знадобитися передати одне або кілька додаткових значень. 
Це може бути якась змінна, об'єкт конфігурації, список чогось, відмітка часу і що завгодно ще. 
Для цього достатньо передати ці дані як іменовані (kwargs) аргументи у диспетчер, або присвоїти значення, як 
якби ви працювали зі словником.

Така можливість найкраще підходить для передачі об'єктів, які повинні жити в єдиному екземплярі і не змінюватися 
у ході роботи бота (тобто бути тільки для читання). Якщо передбачається, що значення повинно змінюватися з часом, то пам'ятайте, що 
це спрацює тільки з [мутабельними об'єктами](https://mathspp.com/blog/pydonts/pass-by-value-reference-and-assignment). 
Щоб отримати значення у хендлерах, просто вкажіть їх як аргументи. Розглянемо на прикладі:

```python
# Десь в іншому місці
# Наприклад, у точці входу у додаток
from datetime import datetime

# bot = ...
dp = Dispatcher()
dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
await dp.start_polling(bot, mylist=[1, 2, 3])


@dp.message(Command("add_to_list"))
async def cmd_add_to_list(message: types.Message, mylist: list[int]):
    mylist.append(7)
    await message.answer("Додано число 7")


@dp.message(Command("show_list"))
async def cmd_show_list(message: types.Message, mylist: list[int]):
    await message.answer(f"Ваш список: {mylist}")

    
@dp.message(Command("info"))
async def cmd_info(message: types.Message, started_at: str):
    await message.answer(f"Бот запущено {started_at}")
```

Тепер змінну `started_at` і список `mylist` можна читати і писати у різних хендлерах. А якщо вам потрібно прокидувати 
унікальні для кожного оновлення значення (наприклад, об'єкт сесії СУБД), 
то ознайомтеся з [мідлвеарами](filters-and-middlewares.md#middlewares).

![Аргумент mylist може бути змінений між викликами](../images/uk/quickstart/l01_4_Light.jpg#only-light)
![Аргумент mylist може бути змінений між викликами](../images/uk/quickstart/l01_4_Dark.jpg#only-dark)

## Файли конфігурації {: id="configuration-files" }

Щоб не зберігати токен прямо у коді (раптом ви захочете залити свого бота у публічний репозиторій?) можна винести 
подібні дані в окремий конфігураційний файл. Існує [хороша і адекватна думка](https://t.me/advice17/26), 
що для проду достатньо змінних оточення, однак у рамках цієї книги ми будемо користуватися окремими файлами `.env`, 
щоб трохи спростити собі життя і заощадити читачам час на розгортання демонстраційного проєкту.

Отже, створимо поруч з `bot.py` окремий файл `config_reader.py` з наступним вмістом

```python title="config_reader.py"
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    # Бажано замість str використовувати SecretStr 
    # для конфіденційних даних, наприклад, токена бота
    bot_token: SecretStr

    # Починаючи з другої версії pydantic, налаштування класу налаштувань задаються
    # через model_config
    # У даному випадку буде використовуватися файл .env, який буде прочитаний
    # з кодуванням UTF-8
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


# При імпорті файлу одразу створюється 
# і валідується об'єкт конфігу, 
# який можна далі імпортувати з різних місць
config = Settings()
```

Тепер трохи відредагуємо наш `bot.py`:

```python title="bot.py"
# імпорти
from config_reader import config

# Для записів з типом Secret* необхідно 
# викликати метод get_secret_value(), 
# щоб отримати справжній вміст замість '*******'
bot = Bot(token=config.bot_token.get_secret_value())
```

Нарешті, створимо файл `.env` (з крапкою на початку), де опишемо токен бота:

```title=".env"
BOT_TOKEN = 0000000000:AaBbCcDdEeFfGgHhIiJjKkLlMmNn
```

Якщо все зроблено правильно, то при запуску python-dotenv підвантажить змінні з файлу `.env`, pydantic 
їх провалідує і об'єкт бота успішно створиться з потрібним токеном.

На цьому ми закінчимо знайомство з бібліотекою, а в наступних розділах розглянемо інші "фішки" aiogram і Telegram Bot API.

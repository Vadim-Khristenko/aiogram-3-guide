---
title: Платежі в Telegram
description: Платежі в Telegram
---
    
# Платежі в Telegram {: id="payments" }

!!! info ""
    Використовувана версія aiogram: 3.7.0

З цієї розділу ви дізнаєтесь, як можна реалізувати покупки у своїх Telegram-ботах з допомогою внутрішньої валюти 
[Telegram Stars](https://telegram.org/blog/telegram-stars). 

## Платежі за допомогою Stars {: id="pay-with-stars" }

Починаючи з червня 2024 року, усі платежі за **цифрові продукти та послуги** в Telegram повинні здійснюватися за допомогою нової 
цифрової валюти Telegram Stars. Ми не будемо детально зупинятися на описанні «Зірочок», тим більше що деталі можуть 
змінюватися зі часом. Нововведення досить суперечливе, але, судячи з усього, розробникам ботів доведеться з цим якось 
справлятися далі, тому варто розібратися в технології.

### План робіт {: id="plan" }

Для наочності розробимо бота для прийому добровільних пожертвувань (донатів). Мають підтримуватися пресети
(<code>/&#8288;donate_1</code>, <code>/&#8288;donate_25</code>, <code>/&#8288;donate_50</code>), 
а також введення довільного числа зірочок (<code>/&#8288;donate 777</code>, де число передається як аргумент команди). 
Також зробимо команду <code>/&#8288;refund</code>, щоб користувач міг повернути витрачені Stars на свій телеграм-аккаунт. 
За [вимогою Telegram](https://telegram.org/tos/bot-developers#6-2-1-payment-disputes-for-digital-goods-and-services), 
усі боти, що приймають оплату за цифрові продукти та послуги, **зобов'язані** підтримувати команду <code>/&#8288;paysupport</code>, але оскільки 
на цей рахунок немає додаткових пояснень, то в ній будемо лише повідомляти користувача про команду <code>/&#8288;refund</code>.

### Технології {: id="technologies" }

Насамперед, aiogram, причому версії не нижче 3.7.0. Незважаючи на те, що підтримка методу 
[sendInvoice](https://core.telegram.org/bots/api#sendinvoice) існує вже давно, метод 
[refundStarPayment](https://core.telegram.org/bots/api#refundstarpayment) був доданий лише в Bot API 7.4, що 
відповідає версії 3.7 у aiogram.

Для відображення логів використовується бібліотека [structlog](https://www.structlog.org/en/stable/). 
Її не буде видно в сніпетах у цьому тексті, але в [вихідних текстах до розділу](https://github.com/MasterGroosha/aiogram-3-guide/tree/master/code/09_payments) 
вона є.

Інформаційні тексти, що відправляються ботом, використовують [Project Fluent](https://projectfluent.org/) від Mozilla. 
Крім сніпета з Python-кодом ви будете бачити відповідні рядки локалізації. Щоб спростити собі завдання, 
а вам допомогти сфокусуватися на новому матеріалі, умовимось, що мова користувача ролі не грає; бот завжди буде 
видавати рядки російською мовою з одного файлу.

!!! info ""
    Якщо ви хочете дізнатися більше про локалізацію Telegram-ботів на різні мови без вищеописаних самообмежень, 
    запрошуємо вас на наш [платний курс](https://stepik.org/a/153850?utm_source=aiogram3guide&utm_medium=web&utm_campaign=payments_chapter) 
    на платформі Stepik.

### Пишемо код. Команда /start {: id="command-start" }

За командою <code>/&#8288;start</code> бот повинен видавати такий красивий текст

```fluent
cmd-start =
    Здравствуйте! Спасибо, что решили воспользоваться ботом. 
    Доступны следующие команды:

    • /donate_1: подарить 1 звезду.
    • /donate_25: подарить 25 звёзд.
    • /donate_50: подарить 50 звёзд.
    • /donate <число>: подарить <число> звёзд.
    • /paysupport: помощь с покупками.
    • /refund: возврат платежа (рефанд).
```

Код:

```python
@router.message(CommandStart())
async def cmd_start(
    message: Message,
    l10n: FluentLocalization,
):
    await message.answer(
        l10n.format_value("cmd-start"),
        parse_mode=None,
    )
```

У цього бота за умовчанням включений режим розмітки HTML, але стартове повідомлення не можна відправити з цим режимом, оскільки 
використовується підрядок <code><&#8288;число&#8288;></code>. Тому `parse_mode` виставляється в `None`. Параметр `l10n` – 
це мідлварь для локалізації, яка підкладає в хендлер об'єкт `FluentLocalization`. У будь-якій незрозумілій ситуації дивіться 
в [вихідники](https://github.com/MasterGroosha/aiogram-3-guide/tree/master/code/09_payments) до розділу.

### Команди /donate {: id="commands-donate" }

Далі потрібно зробити команду <code>/&#8288;donate</code> з довільним вибором суми, а також кілька готових пресетів. 
За станом на червень 2024 року максимальне число зірок для покупки – 2500, при створенні інвойса на більшу суму 
Telegram-клієнти починають «ламатися» і не дають придбати нові зірки прямо перед покупкою. Тому обмежимось 
сумою в інтервалі [1;2500] включно.

Різниця між командою-пресетом і звичайною мінімальна; можна об'єднати все в один обробник. Почнемо його писати: 
отримаємо команду і розпарсимо вміст. Для пресетів треба розбити текст самої команди по підкреслення і витягти 
праву половину як число, а для звичайної команди обережно перевіримо, що передано після неї:

```python
@router.message(Command("donate_1"))
@router.message(Command("donate_25"))
@router.message(Command("donate_50"))
@router.message(Command("donate"))
async def cmd_donate(
    message: Message,
    command: CommandObject,
    l10n: FluentLocalization,
):
    # Якщо це команда /donate ЧИСЛО,
    # тоді витягуємо число з тексту команди
    if command.command != "donate":
        amount = int(command.command.split("_")[1])
    # В іншому випадку намагаємось розпарсити користувацький введення
    else:
        # Перевірка на число і на його діапазон
        if (
            command.args is None
            or not command.args.isdigit()
            or not 1 <= int(command.args) <= 2500
        ):
            await message.answer(
                l10n.format_value("custom-donate-input-error")
            )
            # Завершуємо обробку
            return
        amount = int(command.args)
```

Тепер, коли число зірок отримано і проvalidовано, відправимо користувачу інвойс, тобто рахунок на оплату. 
У випадку з Telegram Stars це виглядає наступним чином:

```python
    ### це продовження хендлера з попереднього сніпета! ###

    # Для платежів у Telegram Stars список цін
    # ПОВИНЕН складатися РОВНО з 1 елемента
    prices = [LabeledPrice(label="XTR", amount=amount)]
    await message.answer_invoice(
        title=l10n.format_value("invoice-title"),
        description=l10n.format_value(
            "invoice-description",
            {"starsCount": amount}
        ),
        prices=prices,
        # provider_token повинен бути порожнім
        provider_token="",
        # У пейлоуд можна передати що угодно,
        # наприклад, айді того, що саме купується
        payload=f"{amount}_stars",
        # XTR - це код валюти Telegram Stars
        currency="XTR"
    )
```

![введення суми донату](../images/ru/payments/cmd_donate.png)

Кнопка "Оплатити" разом із сумою генерується телеграмом автоматично, її не потрібно генерувати вручну. 
Але за бажанням можна створити власну інлайн-клавіатуру і прикріпити її до інвойса. Головна вимога: першою повинна бути 
кнопка з параметром `pay=True`. Якщо в тексті кнопки використовувати емодзі ⭐ або підрядок XTR, то цей текст буде 
автоматично замінено на іконку Telegram Star:

```python
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Оплатити {amount} XTR",
        pay=True
    )
    builder.button(
        text="Скасувати покупку",
        callback_data="cancel"
    )
    builder.adjust(1)

    prices = [LabeledPrice(label="XTR", amount=amount)]
    await message.answer_invoice(
        title=l10n.format_value("invoice-title"),
        description=l10n.format_value(
            "invoice-description",
            {"starsCount": amount}
        ),
        prices=prices,
        provider_token="",
        payload=f"{amount}_stars",
        currency="XTR",
        # Переозначуємо клавіатуру
        reply_markup=builder.as_markup()
    )
```

![інвойс з додатковими кнопками](../images/ru/payments/extra_buttons_invoice.jpg)

Крім того, інвойс можна відправити і як кліцабельне посилання в тексті повідомлення:

```python
@router.message(Command("donate_link"))
async def cmd_link(
    message: Message,
    bot: Bot,
    l10n: FluentLocalization,
):
    # Приклад посилання на інвойс в 1 зірку
    # У відповідь на цей API-виклик, Telegram повертає 
    # одразу посилання.
    invoice_link = await bot.create_invoice_link(
        title=l10n.format_value("invoice-title"),
        description=l10n.format_value(
            "invoice-description",
            {"starsCount": 1}
        ),
        prices=[LabeledPrice(label="XTR", amount=1)],
        provider_token="",
        payload="demo",
        currency="XTR"
    )
    await message.answer(
        l10n.format_value(
            "invoice-link-text",
            {"link": invoice_link}
        )
    )
```

Нові рядки в локалізації:

```fluent
invoice-title = Добровольное пожертвование
invoice-description =
    {$starsCount ->
        [one] {$starsCount} звезда
        [few] {$starsCount} звезды
       *[other] {$starsCount} звёзд
}

custom-donate-input-error = 
    Пожалуйста, введите сумму в формате <code>/donate ЧИСЛО</code>, 
    где ЧИСЛО от 1 до 2500 включительно.

invoice-link-text =
    Воспользуйтесь <a href="{$link}">этой ссылкой</a> для доната в размере 1 звезды.
```

### Перевірка перед оплатою {: id="pre-checkout" }

Якщо у користувача достатньо Зірок на рахунку, то Bot API відправляє боту апдейт типу 
[PreCheckoutQuery](https://core.telegram.org/bots/api#precheckoutquery). У бота є рівно 10 секунд, щоб ще раз 
все перевірити і або підтвердити покупку, або скасувати її. Навіщо скасовувати? Наприклад, користувач намагався купити один 
і той же унікальний елемент двічі. Або він забанений у боті і не повинен мати можливість нічого купувати. Щось угодно. 
Якщо варто скасувати покупку, то бот повинен відповісти на PreCheckoutQuery з `ok=False` і зрозумілим текстом помилки. Наприклад: 

```python
# Текст помилки в FTL-файлі:
pre-checkout-failed-reason = Нет больше места для денег 😭

# Обробник на Python:
@router.pre_checkout_query()
async def on_pre_checkout_query(
    pre_checkout_query: PreCheckoutQuery,
    l10n: FluentLocalization,
):
    await pre_checkout_query.answer(
        ok=False,
        error_message=l10n.format_value("pre-checkout-failed-reason")
    )
```

У цьому випадку бот побачить щось таке:

![Помилка на pre checkout](../images/ru/payments/pre_checkout_failed.png)

Але частіше за все все буде добре і можна дозволити оплату:

```python
@router.pre_checkout_query()
async def on_pre_checkout_query(
    pre_checkout_query: PreCheckoutQuery,
):
    await pre_checkout_query.answer(ok=True)
```

### Після оплати {: id="after-payment" }

Після завершення покупки бот отримає апдейт типу Message з непустим атрибутом `successful_payment`, у вмісті якого 
можна знайти айді транзакції, пейлоуд (технічні дані, які розробник сам передає при створенні інвойса) і 
інші штуки. Наприклад, можна поздоровити користувача з покупкою, додавши до повідомлення ефект вогню, надіслати ID 
для подальшого рефанду (якщо застосовно), або одразу повернути Зірку у випадку з демонстраційними ботами. 

```python
@router.message(F.successful_payment)
async def on_successful_payment(
    message: Message,
    l10n: FluentLocalization,
):
    await message.answer(
        l10n.format_value(
            "payment-successful",
            {"id": message.successful_payment.telegram_payment_charge_id}
        ),
        # Це ефект "вогонь" зі стандартних реакцій
        message_effect_id="5104841245755180586",
    )
```

Оновлюємо локалізацію:

```fluent
payment-successful =
    <b>Величезне спасибі!</b>

    Ваш айді транзакції:
    <code>{$id}</code>

    Збережіть його, якщо раптом зробити рефанд у майбутньому 😢
```

![type:video](../images/ru/payments/payment_video.MP4){: style='height: 50%; width: 50%'}

### Повернення покупок {: id="refunds" }

!!! warning "Обмеження системи рефандів"
    У 2025 році зі мною трапилася смішна історія: мені почали стукатися в особисту кілька людей 
    з проханням повернути витрачені зірки. Проблема в тому, що таких транзакцій у моєму боті 
    [@GrooshaDonateBot](https://t.me/GrooshaDonateBot) немає. Після чергового такого питання з'ясувалось, що люди 
    тратили свої зірки в інших ботах, видимо, не отримували оплачені товари/послуги і шукали в інтернеті як 
    повернути кошти. І AI Overview в Google на запит "який бот в тг допоможе з поверненням зірок витрачених" 
    показував наступний текст: "Для повернення зірок, витрачених за оплату, можна використовувати тестового бота 
    @GrooshaDonateBot або @DurgerKingBot, які повертають витрачену зірку після покупки..."

    Так от. Google (і інші LLM) – рефанд можна __спробувати__ зробити тільки в тому боті, в якому користувач ці 
    зірки витратив. Зірки, витрачені в @BotOne не можна повернути ботом @BotTwo! 

    Achievement Unlocked: _затролен нейронкою_

Строго кажучи, перед початком користування ботом користувач повинен мати можливість ознайомитися з умовами (Terms of Service). 
Зокрема, там повинно бути чітко прописано, за що можна повертати кошти, а за що не можна. Наприклад, ви можете 
одразу повідомити, що за якийсь цифровий товар рефанди (повернення) не передбачені, або що повернення стає 
недоступним після деякої кількості використань послуги або проминулих днів. Про це рішати тільки вам, у нашому 
демонстраційному боті ми дамо користувачу можливість повертати кошти за будь-яку покупку. Для цього реалізуємо команду 
<code>/&#8288;refund</code>, аргументом до якої попросимо передати айді транзакції. Метод 
[refundStarPayment](https://core.telegram.org/bots/api#refundstarpayment) може повернути різні помилки, зокрема, про те, 
що ID транзакції некоректний або що кошти за покупку в конкретній транзакції вже були повернені. 
Обробимо ці випадки і реалізуємо рефанди:

```python
@router.message(Command("refund"))
async def cmd_refund(
    message: Message,
    bot: Bot,
    command: CommandObject,
    l10n: FluentLocalization,
):
    transaction_id = command.args
    if transaction_id is None:
        await message.answer(
            l10n.format_value("refund-no-code-provided")
        )
        return
    try:
        await bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=transaction_id
        )
        await message.answer(
            l10n.format_value("refund-successful")
        )
    except TelegramBadRequest as error:
        if "CHARGE_NOT_FOUND" in error.message:
            text = l10n.format_value("refund-code-not-found")
        elif "CHARGE_ALREADY_REFUNDED" in error.message:
            text = l10n.format_value("refund-already-refunded")
        else:
            # При всіх інших помилках – такий же текст,
            # як і в першому випадку
            text = l10n.format_value("refund-code-not-found")
        await message.answer(text)
        return
```

Рядом напишемо обробник команди <code>/&#8288;paysupport</code>, просто перенаправляючий на <code>/&#8288;refund</code>:

```python
@router.message(Command("paysupport"))
async def cmd_paysupport(
    message: Message,
    l10n: FluentLocalization
):
    await message.answer(l10n.format_value("cmd-paysupport"))
```

Текстів потрібно буде додати на цей раз більше: 

```fluent
refund-successful =
    Повернення здійснено успішно. Витрачені зірки вже повернулись на ваш рахунок у Telegram.

refund-no-code-provided =
    Будь ласка, введіть команду <code>/refund КОД</code>, де КОД – айді транзакції.
    Його можна побачити після виконання платежу, а також в розділі "Зірки" в додатку Telegram.

refund-code-not-found =
    Такий код покупки не знайдено. Будь ласка, перевірте вводимі дані і повторіть ще раз.

refund-already-refunded =
    За цю покупку вже раніше було здійснено повернення коштів.

cmd-paysupport =
    Якщо ви хочете повернути кошти за покупку, скористайтесь командою /refund
```

Результат:

![успішне повернення коштів](../images/ru/payments/refunds.png)

!!! info "Спробувати бота в дії"
    Ви можете спробувати оплату за допомогою Telegram Stars у боті [@GrooshaDonateBot](https://t.me/GrooshaDonateBot). 
    Вам знадобляться Зірки для будь-якої транзакції, але якщо скористаєтесь командою <code>/&#8288;demo</code>, то 
    платіж у фіксованому розмірі 1 зірки одразу ж повернеться назад на ваш аккаунт після покупки.

Тепер ви готові реалізовувати оплату за цифрові товари та послуги у своїх ботах за допомогою Telegram Stars, ура!

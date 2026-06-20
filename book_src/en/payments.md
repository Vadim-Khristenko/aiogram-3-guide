---
title: Payments in Telegram
description: Payments in Telegram
---
    
# Payments in Telegram {: id="payments" }

!!! info ""
    aiogram version used: 3.7.0

In this chapter, you will learn how to implement purchases in your Telegram bots using the internal currency
[Telegram Stars](https://telegram.org/blog/telegram-stars). 

## Payments Using Stars {: id="pay-with-stars" }

Since June 2024, all payments for **digital products and services** in Telegram must be made using the new 
digital currency Telegram Stars. We won't go into detail about Stars, as the details may change over time. 
The innovation is quite controversial, but it appears that bot developers will have to adapt to it, 
so it's worth understanding the technology.

### Work Plan {: id="plan" }

For clarity, we will develop a bot for accepting voluntary donations. It should support presets
(<code>/&#8288;donate_1</code>, <code>/&#8288;donate_25</code>, <code>/&#8288;donate_50</code>), 
as well as custom amounts (<code>/&#8288;donate 777</code>, where the number is passed as a command argument). 
We will also implement a <code>/&#8288;refund</code> command so users can return spent Stars to their Telegram account. 
According to [Telegram requirements](https://telegram.org/tos/bot-developers#6-2-1-payment-disputes-for-digital-goods-and-services), 
all bots accepting payments for digital products and services **must** support the <code>/&#8288;paysupport</code> command, but since 
there are no additional explanations for it, we will simply notify the user about the <code>/&#8288;refund</code> command.

### Technologies {: id="technologies" }

First and foremost, aiogram, version 3.7.0 or higher. While support for the 
[sendInvoice](https://core.telegram.org/bots/api#sendinvoice) method has existed for a while, the 
[refundStarPayment](https://core.telegram.org/bots/api#refundstarpayment) method was added only in Bot API 7.4, 
which corresponds to version 3.7 in aiogram.

For log display, we use the [structlog](https://www.structlog.org/en/stable/) library. 
It won't be visible in the code snippets in this text, but it is present in the [source code for this chapter](https://github.com/MasterGroosha/aiogram-3-guide/tree/master/code/09_payments).

The informational texts sent by the bot use [Project Fluent](https://projectfluent.org/) from Mozilla. 
Besides Python code snippets, you will see corresponding localization strings. To simplify our task 
and help you focus on the new material, let's assume that user language doesn't matter; the bot will always 
return strings in Russian from a single file.

!!! info ""
    If you want to learn more about localizing Telegram bots for multiple languages without the above limitations, 
    we invite you to our [paid course](https://stepik.org/a/153850?utm_source=aiogram3guide&utm_medium=web&utm_campaign=payments_chapter) 
    on the Stepik platform.

### Writing Code. `/start` Command {: id="command-start" }

On the `/start` command, the bot should display a nice text like this:

```fluent
cmd-start =
    Hello! Thank you for using the bot. 
    Available commands:

    • /donate_1: donate 1 star.
    • /donate_25: donate 25 stars.
    • /donate_50: donate 50 stars.
    • /donate <number>: donate <number> stars.
    • /paysupport: help with purchases.
    • /refund: payment refund.
```

Code:

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

This bot has HTML markup mode enabled by default, but the start message cannot be sent with this mode, since 
the substring <code><&#8288;number&#8288;></code> is used. Therefore, `parse_mode` is set to `None`. The `l10n` parameter – 
is a middleware for localization that supplies the handler with a `FluentLocalization` object. If anything is unclear, 
check the [source code](https://github.com/MasterGroosha/aiogram-3-guide/tree/master/code/09_payments) for this chapter.

### `/donate` Commands {: id="commands-donate" }

Next, we need to implement the <code>/&#8288;donate</code> command with a custom amount selection, as well as several ready-made presets. 
As of June 2024, the maximum number of stars for purchase is 2500; when creating an invoice for a larger amount, 
Telegram clients start to "break" and won't allow new stars to be purchased right before the transaction. So we'll limit ourselves 
to amounts in the range [1;2500] inclusive.

The difference between a preset command and a regular one is minimal; we can combine everything into one handler. Let's start writing it: 
we'll get the command and parse its contents. For presets, we need to split the command text by underscore and extract 
the right half as a number, and for a regular command, we'll carefully check what was passed after it:

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
    # If this is a /donate NUMBER command,
    # extract the number from the command text
    if command.command != "donate":
        amount = int(command.command.split("_")[1])
    # Otherwise, try to parse user input
    else:
        # Check that it's a number and in the correct range
        if (
            command.args is None
            or not command.args.isdigit()
            or not 1 <= int(command.args) <= 2500
        ):
            await message.answer(
                l10n.format_value("custom-donate-input-error")
            )
            # End processing
            return
        amount = int(command.args)
```

Now that we have obtained and validated the number of stars, let's send the user an invoice, i.e., a payment request. 
In the case of Telegram Stars, it looks like this:

```python
    ### this is a continuation of the handler from the previous snippet! ###

    # For Telegram Stars payments, the price list
    # MUST consist of EXACTLY 1 element
    prices = [LabeledPrice(label="XTR", amount=amount)]
    await message.answer_invoice(
        title=l10n.format_value("invoice-title"),
        description=l10n.format_value(
            "invoice-description",
            {"starsCount": amount}
        ),
        prices=prices,
        # provider_token must be empty
        provider_token="",
        # You can pass anything to the payload,
        # for example, the ID of what is being purchased
        payload=f"{amount}_stars",
        # XTR is the currency code for Telegram Stars
        currency="XTR"
    )
```

![donation amount input](../images/ru/payments/cmd_donate.png)

The "Pay" button along with the amount is generated by Telegram automatically; you don't need to generate it manually. 
But if you wish, you can create your own inline keyboard and attach it to the invoice. The main requirement: the first button 
should have the parameter `pay=True`. If you use the emoji ⭐ or the substring XTR in the button text, this text will 
be automatically replaced with the Telegram Star icon:

```python
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Pay {amount} XTR",
        pay=True
    )
    builder.button(
        text="Cancel purchase",
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
        # Override the keyboard
        reply_markup=builder.as_markup()
    )
```

![invoice with additional buttons](../images/ru/payments/extra_buttons_invoice.jpg)

By the way, an invoice can also be sent as a clickable link in a message:

```python
@router.message(Command("donate_link"))
async def cmd_link(
    message: Message,
    bot: Bot,
    l10n: FluentLocalization,
):
    # Example of a link to an invoice for 1 star
    # In response to this API call, Telegram returns 
    # the link right away.
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

New strings in localization:

```fluent
invoice-title = Voluntary donation
invoice-description =
    {$starsCount ->
        [one] {$starsCount} star
        [few] {$starsCount} stars
       *[other] {$starsCount} stars
}

custom-donate-input-error = 
    Please enter the amount in the format <code>/donate NUMBER</code>, 
    where NUMBER is from 1 to 2500 inclusive.

invoice-link-text =
    Use <a href="{$link}">this link</a> to donate 1 star.
```

### Pre-Payment Check {: id="pre-checkout" }

If the user has enough Stars in their account, Bot API sends the bot an update of type 
[PreCheckoutQuery](https://core.telegram.org/bots/api#precheckoutquery). The bot has exactly 10 seconds to verify everything again 
and either confirm the purchase or cancel it. Why cancel? For example, a user tried to buy the same unique item twice. 
Or they are banned in the bot and shouldn't be able to purchase anything. Anything is possible. 
If the purchase should be cancelled, the bot must respond to the PreCheckoutQuery with `ok=False` and a clear error message. For example:

```python
# Error message in the FTL file:
pre-checkout-failed-reason = No more room for money 😭

# Handler in Python:
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

In this case, the user will see something like this:

![Error on pre-checkout](../images/ru/payments/pre_checkout_failed.png)

But most of the time everything will be fine and you can allow the payment:

```python
@router.pre_checkout_query()
async def on_pre_checkout_query(
    pre_checkout_query: PreCheckoutQuery,
):
    await pre_checkout_query.answer(ok=True)
```

### After Payment {: id="after-payment" }

After the purchase is completed, the bot receives a Message update with a non-empty `successful_payment` attribute, 
which contains the transaction ID, payload (technical data that the developer himself passes when creating the invoice), and 
other information. For example, you can congratulate the user on the purchase by adding a fire effect to the message, 
send an ID for future refunds (if applicable), or immediately return the Star in the case of demo bots.

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
        # This is the "fire" effect from standard reactions
        message_effect_id="5104841245755180586",
    )
```

Update the localization:

```fluent
payment-successful =
    <b>Thank you very much!</b>

    Your transaction ID:
    <code>{$id}</code>

    Save it in case you need a refund in the future 😢
```

![type:video](../images/ru/payments/payment_video.MP4){: style='height: 50%; width: 50%'}

### Payment Refunds {: id="refunds" }

!!! warning "Refund System Limitations"
    In 2025, something funny happened to the author of this text: various people started messaging me asking to 
    return their spent stars. The problem was that there were no such transactions in my bot 
    [@GrooshaDonateBot](https://t.me/GrooshaDonateBot). After another such question, it turned out that people 
    were spending their stars in other bots, apparently not receiving the paid goods/services, and searching the internet 
    for how to return funds. And Google's AI Overview for the query "which bot in Telegram can help return spent stars" 
    showed the following text: "To return stars spent on payment, you can use the test bot 
    @GrooshaDonateBot or @DurgerKingBot, which return the spent star after purchase..."

    So here's the thing. Google (and other LLMs) – a refund can __only be attempted__ in the bot where the user spent the 
    stars. Stars spent in @BotOne cannot be refunded by @BotTwo! 

    Achievement Unlocked: _trolled by an AI_

Strictly speaking, before using the bot, a user should be able to review the Terms of Service. 
In particular, it should clearly state what can and cannot be refunded. For example, you can immediately tell the user 
that refunds are not provided for some digital goods, or that refunds become unavailable after a certain number of uses 
or days. It's up to you to decide. In our demonstration bot, we will give the user the ability to refund any purchase. 
To do this, we implement the <code>/&#8288;refund</code> command, which takes the transaction ID as an argument. The 
[refundStarPayment](https://core.telegram.org/bots/api#refundstarpayment) method can return various errors, in particular, 
about an incorrect transaction ID or that funds for the purchase in that particular transaction have already been refunded. 
Let's handle these cases and implement refunds:

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
            # For all other errors – the same text
            # as in the first case
            text = l10n.format_value("refund-code-not-found")
        await message.answer(text)
        return
```

Next to it, let's write a handler for the <code>/&#8288;paysupport</code> command that simply redirects to <code>/&#8288;refund</code>:

```python
@router.message(Command("paysupport"))
async def cmd_paysupport(
    message: Message,
    l10n: FluentLocalization
):
    await message.answer(l10n.format_value("cmd-paysupport"))
```

This time we need to add more texts to the localization:

```fluent
refund-successful =
    Refund completed successfully. The spent stars have already returned to your Telegram account.

refund-no-code-provided =
    Please enter the command <code>/refund CODE</code>, where CODE is the transaction ID.
    You can see it after completing the payment, as well as in the "Stars" section in the Telegram app.

refund-code-not-found =
    Purchase code not found. Please check the data you entered and try again.

refund-already-refunded =
    A refund for this purchase has already been made.

cmd-paysupport =
    If you want to return funds for a purchase, use the /refund command
```

Result:

![successful refund](../images/ru/payments/refunds.png)

!!! info "Try the bot in action"
    You can try payments using Telegram Stars in the bot [@GrooshaDonateBot](https://t.me/GrooshaDonateBot). 
    You will need Stars for any transaction, but if you use the <code>/&#8288;demo</code> command, a fixed 
    payment of 1 star will be immediately refunded to your account after the purchase.

Now you're ready to implement payments for digital goods and services in your bots using Telegram Stars, hooray!

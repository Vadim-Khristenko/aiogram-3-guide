---
title: Telegram Payments
description: Telegram Payments
---

# Telegram Payments {: id="payments" }

!!! info ""
    aiogram version used: 3.7.0

In this chapter, we implement purchases in Telegram bots using
[Telegram Stars](https://telegram.org/blog/telegram-stars).

## Paying with Stars {: id="pay-with-stars" }

Since June 2024, payments for **digital products and services** in Telegram must use Telegram Stars.
The rules may evolve over time, but for bot developers this is now a practical reality,
so it is important to understand the flow.

### Work plan {: id="plan" }

As a practical project, we build a donation bot with:

- presets (`/donate_1`, `/donate_25`, `/donate_50`),
- custom amount (`/donate 777`),
- `/refund` to return spent Stars.

Telegram also requires bots that sell digital goods/services to provide `/paysupport`
([requirement](https://telegram.org/tos/bot-developers#6-2-1-payment-disputes-for-digital-goods-and-services)).
In this chapter, it additionally reminds users about `/refund`.

### Technologies {: id="technologies" }

- aiogram 3.7.0+ (because `refundStarPayment` appeared in Bot API 7.4)
- [structlog](https://www.structlog.org/en/stable/) for logs
- [Project Fluent](https://projectfluent.org/) for localized text templates

### Writing code. `/start` command {: id="command-start" }

On `/start`, the bot sends a message describing available payment commands.
If your bot globally uses HTML parse mode, remember that command examples with angle brackets
may require `parse_mode=None` for this specific message.

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

### `/donate` commands {: id="commands-donate" }

You can process presets and custom amounts in one handler.
Validate the amount range before creating an invoice.

At the time of writing, practical upper bound is 2500 Stars for a smooth client experience,
so this chapter uses range `[1;2500]`.

Then send invoice via `answer_invoice`:

```python
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
    currency="XTR"
)
```

For Telegram Stars, `prices` must contain **exactly one** element,
`provider_token` must be empty, and currency is `XTR`.

### Successful payments {: id="successful-payment" }

After payment, handle successful transaction updates,
store required metadata, and provide a clean user confirmation message.

### Refunds {: id="refund" }

Implement `/refund` as required by your product policy.
For support workflows, ensure users can quickly discover refund instructions.

## Additional Materials {: id="extras" }

- Source chapter in Russian: `/payments/`
- Example code: `code/ru/09_payments/`
- Telegram payments docs: https://core.telegram.org/bots/payments

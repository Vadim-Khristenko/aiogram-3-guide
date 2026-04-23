---
title: Payments
description: Telegram payments and Stars
---

# Payments {: id="payments" }

!!! info ""
    aiogram version used: 3.7.0  
    Tested with aiogram: 3.27.0 | 24.04.2026

This chapter focuses on integrating payments in Telegram bots, with emphasis on Telegram Stars.

## Paying with Stars {: id="pay-with-stars" }

Typical payment pipeline:

1. Create an invoice and send it to the user.
2. Handle pre-checkout validation.
3. Process successful payment callbacks.
4. Persist entitlement/subscription state.
5. Provide reliable idempotency for repeated events.

Security and reliability recommendations:

- validate payloads and invoice metadata;
- never grant premium access before successful confirmation;
- make purchase handlers idempotent;
- keep auditable payment logs.

## Code and Further Reading

- Russian chapter source: `/payments/`
- Example code base: `code/ru/09_payments/`
- Telegram Bot API payments docs: https://core.telegram.org/bots/payments

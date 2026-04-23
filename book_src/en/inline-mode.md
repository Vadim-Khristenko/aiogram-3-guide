---
title: Inline Mode
description: Inline Mode
---

# Inline Mode

!!! info ""
    aiogram version used: 3.7.0

## Theory {: id="theory" }

### Why do we need inline mode? {: id="why-inline-mode" }

In previous chapters, the bot and the user interacted directly.
Telegram also provides a special mode where a user sends content **on their own behalf**,
but with help from a bot. This is called **Inline mode**.

Inline mode is ideal for searching and inserting content into the current chat.
Classic examples include bots like `@gif`, `@wiki`, `@imdb`, `@youtube`, and others.

!!! warning "Important"
    If a message sent via inline mode has a callback button attached,
    pressing that button gives the bot a `CallbackQuery` **without** a `Message` object.
    Instead, you get `inline_message_id`.

### Incoming update format {: id="incoming-update-format" }

When a user types your bot username in a chat and continues with a query,
Telegram sends an [InlineQuery](https://core.telegram.org/bots/api#inlinequery) update.

Two important details:

- there is no chat ID; instead, there is optional `chat_type`;
- `offset` is a **string**, not a number.

`offset` is used for pagination. Since one response can return at most 50 results,
you pass `next_offset`, and Telegram sends it back as `offset` in the next query.

### Outgoing answer format {: id="outgoing-answer-format" }

There is one API method for replies:
[answerInlineQuery](https://core.telegram.org/bots/api#answerinlinequery),
and many result types ([InlineQueryResult](https://core.telegram.org/bots/api#inlinequeryresult)).

A common type is
[InlineQueryResultArticle](https://core.telegram.org/bots/api#inlinequeryresultarticle).
It is shown as a list of cards with title, optional description, and preview.
When pressed, Telegram sends data from mandatory `input_message_content`.

Media types (for example, `InlineQueryResultPhoto`) also have cached variants.
The difference is simple:

- regular version takes a URL;
- cached version takes Telegram `file_id`.

!!! warning "Important"
    In inline mode, you cannot upload a local image file directly.
    Use either a public URL or an existing Telegram `file_id`.

Useful `answerInlineQuery` arguments:

- `cache_time` — server-side cache lifetime;
- `is_personal` — whether cache is user-specific;
- `next_offset` — pagination token;
- `switch_pm_text` + `switch_pm_parameter` — button above results to jump into PM.

## Practice {: id="practice" }

For practice, this chapter builds a bot that accepts links and images from users,
and later returns them through inline mode.

!!! info ""
    Don’t forget to enable inline mode via [@BotFather](https://t.me/botfather):
    Bot Settings → Inline Mode → Turn on

### Storage system {: id="storage" }

To keep the chapter focused, storage is implemented with an in-memory dictionary
(as a simple database mock).

For each data type (links and images), we define operations to add, get, and delete entries.
This is enough to demonstrate inline-mode mechanics without introducing DB complexity.

## Additional Materials {: id="extras" }

- Source chapter in Russian: `/inline-mode/`
- Example code: `code/ru/08_inline_mode/`
- Telegram docs: https://core.telegram.org/bots/api#inline-mode

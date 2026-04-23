---
title: Inline Mode
description: Inline queries and inline results in aiogram
---

# Inline Mode {: id="inline-mode" }

!!! info ""
    aiogram version used: 3.7.0  
    Tested with aiogram: 3.27.0 | 24.04.2026

Inline mode allows users to interact with your bot from any chat without opening a direct dialog.

## Theory {: id="theory" }

Core objects and concepts:

- inline query events from users;
- result sets (`InlineQueryResult*` variants);
- chosen inline result callbacks;
- pagination and caching.

Design goals:

- fast first response;
- deterministic ranking of results;
- predictable cache behavior;
- graceful handling of empty queries.

## Practice {: id="practice" }

Recommended implementation pattern:

1. Parse and normalize the inline query text.
2. Build results according to query intent.
3. Set cache time intentionally (short for dynamic content).
4. Return compact, high-signal result cards.
5. Log chosen results for quality tuning.

For high-load bots:

- precompute common responses;
- avoid expensive network calls in hot paths;
- use bounded pagination and strict timeouts.

## Additional Materials {: id="extras" }

- Russian chapter source: `/inline-mode/`
- Example code base: `code/ru/08_inline_mode/`
- Telegram Bot API docs: https://core.telegram.org/bots/api#inline-mode

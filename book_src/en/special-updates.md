---
title: Special Updates
description: my_chat_member and chat_member updates
---

# Special Updates {: id="special-updates" }

!!! info ""
    aiogram version used: 3.7.0  
    Tested with aiogram: 3.27.0 | 24.04.2026

This chapter covers service updates that are especially important for moderation, permissions, and bot lifecycle handling in chats.

## Introduction {: id="intro" }

Telegram provides two update types that are crucial for production bots:

- `my_chat_member` — state changes related to the bot itself (added/removed, blocked/unblocked, rights changed).
- `chat_member` — state changes of users in chats where the bot has sufficient rights.

These updates make it possible to avoid blind polling-style checks and react to permission changes in real time.

## ChatMemberUpdated Object {: id="chatmemberupdated" }

Both updates are delivered as `ChatMemberUpdated` objects. The most important fields are:

- `from_user`: who performed the action;
- `old_chat_member`: previous membership/rights state;
- `new_chat_member`: current membership/rights state;
- `invite_link`: optional invitation link context.

Use this object as a diff-like representation of state transitions.

## my_chat_member Update {: id="my-chat-member" }

Use `my_chat_member` handlers to:

- detect when the bot is added to or removed from groups/channels;
- handle user blocks/unblocks in private chats;
- detect permission restrictions for the bot;
- disable features when posting rights are lost.

A practical recommendation: maintain a per-chat capability cache and refresh it on each relevant transition.

## chat_member Update {: id="chat-member" }

Use `chat_member` handlers to:

- track joins/leaves for onboarding and cleanup;
- detect promotions/demotions of administrators;
- update local permission models;
- trigger moderation routines only when rights and context are valid.

!!! warning "Important"
    By default, `chat_member` updates are not always enabled in every bot setup. Ensure your update handling and dispatcher configuration explicitly include them.

## Code and Further Reading

- Russian chapter source: `/special-updates/`
- aiogram docs: https://docs.aiogram.dev/en/dev-3.x/dispatcher/filters/chat_member_updated.html
- Example code base: `code/ru/06_special_updates/`

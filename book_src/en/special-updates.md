---
title: Special Updates my_chat_member and chat_member
description: Special updates my_chat_member and chat_member
---

# Special Updates {: id="special-updates" }

!!! info ""
    aiogram version used: 3.7.0

## Introduction {: id="intro" }

Almost every kind of Telegram event has some visible representation for the user: service messages, regular messages,
callbacks, inline mode, and so on. But there are two update types that are primarily intended for bots themselves:
`my_chat_member` and `chat_member`.

Back in the day, bots in groups existed in an “information vacuum.” For almost any moderation action — bans,
restrictions, and similar changes — developers had to call
[getChatMember](https://core.telegram.org/bots/api#getchatadministrators)
or [getChatAdministrators](https://core.telegram.org/bots/api#getchatadministrators),
and often cache results for a short time to avoid hitting Bot API limits.

Another common edge case: a user adds a bot to a group, removes its permission to send messages, and then starts
triggering commands, expecting the bot to fail. Direct messages had similar issues: without reliable status tracking,
many bots had to probe users manually (for example, by sending a `ChatAction`) and infer blocks from API errors.

In March 2021, with
[Bot API v5.1](https://core.telegram.org/bots/api-changelog#march-9-2021),
this improved significantly. Telegram introduced two new update types: `my_chat_member` and `chat_member`.
Both contain the same object type:
[ChatMemberUpdated](https://core.telegram.org/bots/api#chatmemberupdated).
The practical difference is:

* `my_chat_member` — changes related to the bot itself (or a private chat with the bot):
  user blocks/unblocks, bot added/removed from groups/channels, bot rights changed, etc.
* `chat_member` — changes for users in groups/channels where the bot is an administrator:
  joins/leaves, subscriptions/unsubscriptions, role and rights changes, admin promotions/demotions, and more.

!!! warning "Important"
    By default, Telegram does not always deliver `chat_member` updates unless they are explicitly enabled for your bot.
    See details in the [relevant section](#chat-member).

In this chapter, we focus on the most common practical scenarios. Before going deeper, it is highly recommended to read
[this page](https://docs.aiogram.dev/en/dev-3.x/dispatcher/filters/chat_member_updated.html)
in the **aiogram 3.x** documentation.

## ChatMemberUpdated Object {: id="chatmemberupdated" }

The [ChatMemberUpdated](https://core.telegram.org/bots/api#chatmemberupdated) object deserves special attention.
Suppose, in a group, admin Alice bans user Bob. Fields `chat` and `date` are straightforward, so let’s skip them.

Field `from` (named `from_user` in Python code) contains the subject of the action.
In our example, that is Alice, so this field is a [User](https://core.telegram.org/bots/api#user) object with Alice’s data.

`old_chat_member` and `new_chat_member` represent the state **before** and **after** the event:

- `old_chat_member`: for example, [ChatMemberMember](https://core.telegram.org/bots/api#chatmembermember)
- `new_chat_member`: for example, [ChatMemberBanned](https://core.telegram.org/bots/api#chatmemberbanned)

Both include a `user` field for the same user whose status changed.

If someone joins via an invite link, `ChatMemberUpdated` may also contain a non-empty
`invite_link` field of type [ChatInviteLink](https://core.telegram.org/bots/api#chatinvitelink),
showing which link was used.

!!! warning "About invite links"
    There is an important nuance: each admin (including bots) can create multiple invite links with different settings.
    If a user joins through a link created by your bot, the bot can usually see that link in full.
    If the link belongs to another admin, Telegram may expose only part of it.

## my_chat_member Update {: id="my-chat-member" }

In practice, `my_chat_member` is most useful for tracking:

- bot block/unblock events in private chats;
- bot being added to or removed from groups/channels;
- rights changes that affect bot behavior.

A common case is maintaining an up-to-date list of users who can still receive direct notifications from the bot.

## chat_member Update {: id="chat-member" }

`chat_member` is useful when your bot moderates or monitors chat membership:

- user joins/leaves in groups;
- admin role changes;
- rights transitions and restrictions;
- channel subscription changes.

When implementing handlers, think in terms of state transitions (before → after),
not only “current status.” This usually leads to cleaner and more reliable logic.

## Additional Materials {: id="extras" }

- Source chapter in Russian: `/special-updates/`
- aiogram docs: https://docs.aiogram.dev/en/dev-3.x/dispatcher/filters/chat_member_updated.html
- Example code: `code/ru/06_special_updates/`

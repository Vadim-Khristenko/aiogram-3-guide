---
title: my_chat_member and chat_member Updates
description: my_chat_member and chat_member Updates
---

# Special Updates {: id=”special-updates” }

!!! info “”
    aiogram version used: 3.7.0

## Introduction {: id=”intro” }

Nearly all types of events in Telegram have some external representation for the user. Service messages, regular messages, 
callbacks, inline mode... but there are two types of updates designed specifically for the bots themselves. We’re talking about 
`my_chat_member` and `chat_member`.

Once upon a time, bots in groups existed in an “information vacuum”: basically, for any moderator actions, whether bans or 
restrictions, it was necessary to check the rights of the user making the call through the methods 
[getChatMember](https://core.telegram.org/bots/api#getchatadministrators) or 
[getChatAdministrators](https://core.telegram.org/bots/api#getchatadministrators), and also cache the result for a short period 
to avoid hitting the Bot API limits, the exact values of which remain a mystery. 

Or, for example, some clever user might add a bot to a group, remove its write permission, and start sending commands, expecting 
the bot not to handle the error and crash. And with sending to private chats, things were even trickier: without knowing exactly 
what the bot’s active user base was, developers had to either send some message to all users in their database, or, which is 
slightly more humane, send these users some ChatAction like “_typing..._”; it turned out that those who blocked the bot wouldn’t receive 
this “_typing..._”, returning an error from the Bot API.

In March 2021, the situation changed dramatically for the better with the release of 
[Bot API v5.1 update](https://core.telegram.org/bots/api-changelog#march-9-2021), which 
added two new types of updates: `my_chat_member` and `chat_member`. Both updates 
contain an object of the same type [ChatMemberUpdated](https://core.telegram.org/bots/api#chatmemberupdated). 
The difference between these two events is as follows:

* `my_chat_member`. Here everything that concerns the bot directly or a private chat with the user: blocking/unblocking 
the bot by the user in private chat, adding the bot to a group or channel, removing it from there, changing the bot’s rights 
and status in different chats, etc.
* `chat_member`. Contains all changes in the status of users in groups and channels where the bot is an administrator: 
users joining/leaving groups, subscribing/unsubscribing from channels, changes in user rights and statuses, 
assigning/removing admins, and much more.

!!! warning “Important”
    By default, Telegram does not send `chat_member` updates to bots; you need to enable receiving them separately. More details — 
    in the [corresponding section](#chat-member)

In this chapter, we’ll try to consider these updates for the most commonly needed tasks, but before moving to the next sections, 
I strongly recommend familiarizing yourself with 
[this page](https://docs.aiogram.dev/en/dev-3.x/dispatcher/filters/chat_member_updated.html) 
from the **aiogram 3.x** documentation.

## ChatMemberUpdated Object {: id=”chatmemberupdated” }

The [ChatMemberUpdated](https://core.telegram.org/bots/api#chatmemberupdated) object itself deserves special attention. 
To study it more closely, let’s assume that in a certain group, administrator Alice banned regular member Vitya. 
With the `chat` and `date` fields, everything is obvious, we’ll skip them.

The `from` field (in your Python code this will be `from_user`) contains information about the subject of the action. 
In our case, the subject of the action is Alice, so in `from` (`from_user`) there will be a [User](https://core.telegram.org/bots/api#user) 
object with Alice’s data.

`old_chat_member` and `new_chat_member`. These fields hide the “states” 
of the action subject BEFORE and AFTER the event. Accordingly, in `old_chat_member` there will be an object of type 
[ChatMemberMember](https://core.telegram.org/bots/api#chatmembermember) (this is not a typo), and a `user` field with information 
about Vitya, and in `new_chat_member` — a [ChatMemberBanned](https://core.telegram.org/bots/api#chatmemberbanned) object with the 
`user` field still containing information about the unfortunate Viktor.

Finally, if a hypothetical Masha joined the group or channel, then in the ChatMemberUpdated object there will be a non-empty 
`invite_link` field of type [ChatInviteLink](https://core.telegram.org/bots/api#chatinvitelink) with information about which 
invite link she used to join. 

!!! warning “About Invite Links”
    It’s worth noting here that each administrator of a group/channel (including bots) can create multiple invite links with 
    different parameters. If the bot “caught” a user joining via an invite link created by the bot itself, then in the `invite_link` 
    field of the ChatInviteLink object, the link will be visible in full (without `https://t.me`, of course). But if a user came 
    through another administrator’s link, the bot will only see the first part, with the second part replaced by ellipsis. 
    
    Most likely, this was done to prevent bots from sending invite links created by other chat administrators to just anyone.

    Interestingly, due to some quirky Telegram logic, if you join a public group through an invite link 
    (even if not by username), the bot won’t see the link (will get `None`). Telegram 🤷‍♂️

## my_chat_member Update {: id=”my-chat-member” }

### Bans/Unbans in Private Chat {: id=”ban-unban-pm” }

In specialized chats, the question periodically arises: “how do I make a broadcast to bot users 
if someone might have blocked it?”. Of course, the first and main advice would be: 
“create a [channel](https://telegram.org/faq_channels)”, because channels are the best way to inform users 
about something.

But if you’ve still firmly decided to broadcast to users directly through the bot, there are three main 
ways to keep the list of active bot users up to date:

1. Directly during the broadcast by catching sending errors and making changes to the user database.
2. Through periodic [sending of some ChatAction](https://core.telegram.org/bots/api#sendchataction), 
for example, “typing” to the list of users.
3. By listening to the my_chat_member update.

Now we’re only interested in item 3. Let’s learn to use `my_chat_member` to determine that a user 
has blocked or unblocked the bot. But before we try aiogram “magic”, let’s figure out how the mentioned situations 
look in the Bot API itself. To do this, we’ll stop the bot process, open a dialog with it in Telegram, and sequentially 
block and unblock it using the options in the messenger’s UI. Then we’ll open a web browser or some 
Insomnia/Postman tool and go to the URL `https://api.telegram.org/bot<TOKEN>/getupdates` to see the unprocessed messages 
in JSON format.

So, here’s what the bot receives when someone blocks it:

![User blocked the bot](../images/ru/special-updates/my_chat_member-blocked.png)

Things to pay attention to:

* The `my_chat_member` event occurred in a private chat with the user Groosha (chat_id equals my Telegram ID).
* The initiator (subject) of the event is also Groosha.
* In the `old_chat_member` field, we can see who the action was performed on (the bot) and what status the bot had in the private chat BEFORE: “member”, 
i.e., the bot was NOT blocked before.
* In the `new_chat_member` field, the `user` contents are the same, but the status is now “kicked”, i.e., AFTER the event the bot was 
blocked by the user.

That is, the bot in the private chat with Groosha made a transition from “member” to “kicked” status. Now let’s see what came from 
Telegram after unblocking:

![User unblocked the bot](../images/ru/special-updates/my_chat_member-unblocked.png)

This screenshot is similar to the previous one, but if you look closely, you can notice a difference: different `update_id` 
(increased by one), and also the statuses before and after have swapped places. The bot in the private chat with Groosha made a transition 
from “kicked” to “member”.  
Additionally, there will usually be another update with type `message` and the `/start` 
command in the content. Official clients send the `/start` command immediately when unblocking the bot, but don’t rely on this: 
such actions are left to the clients, which may behave differently.

Now let’s learn to react to such events through aiogram with a simple example: suppose we have a list of two active 
bot users with IDs 111 and 222. With the `/start` command, we’ll add the user to the broadcast list, and with the `/users` 
command, we’ll display the IDs of those who haven’t blocked the bot (in other words, when the bot is blocked, we’ll remove the ID 
from the list, and when unblocked, we’ll add it again).

Here’s a ready-made router for the conditions described above:

```python title=”handlers/in_pm.py”
from aiogram import F, Router
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.filters.command import \
    CommandStart, Command
from aiogram.types import ChatMemberUpdated, Message

router = Router()
router.my_chat_member.filter(F.chat.type == “private”)
router.message.filter(F.chat.type == “private”)

# For example purposes only!
# In real life, use more reliable
# sources of user IDs
users = {111, 222}


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def user_blocked_bot(event: ChatMemberUpdated):
    users.discard(event.from_user.id)


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=MEMBER)
)
async def user_unblocked_bot(event: ChatMemberUpdated):
    users.add(event.from_user.id)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(“Hello”)
    users.add(message.from_user.id)


@router.message(Command(“users”))
async def cmd_users(message: Message):
    await message.answer(“\n”.join(f”• {user_id}” for user_id in users))

```

Pay attention: for handlers on the `my_chat_member` update, we use the `ChatMemberUpdatedFilter` filter with 
specifying the result we’re catching AFTER (i.e., the `new_chat_member` attribute of the update). That is, in this case, 
we don’t care what state the user was in BEFORE.

And here’s how it looks in practice:

![type:video](../images/ru/special-updates/my_chat_member_video.mp4)

### Adding to a Group {: id=”bot-added-to-group” }

Another common question from beginner developers: “how do I catch the event of the bot being added to a group?”. Well, 
let’s figure it out. But first, let’s look at what the possible 
“[statuses](https://core.telegram.org/bots/api#chatmember)” of a user can be:

* creator (also owner) — chat owner. It seems that a bot cannot have such a status. The owner unconditionally has 
all possible rights in the chat except “anonymity”, which can be switched freely.
* administrator — any other administrator. In the application interface, you can remove all their rights, 
but they will still remain an administrator and can, for example, view Recent Actions and ignore slow mode.
* member — chat participant with default rights. These “default rights” for groups can be found by calling 
the [getChat](https://core.telegram.org/bots/api#getchat) API method and looking at the `permissions` field.
* restricted — a user with restrictions on certain rights. For example, in so-called “read-only” mode. 
**IMPORTANT**: in the `restricted` state, a user can both be in the group and not be in it, so 
with [ChatMemberRestricted](https://youtu.be/ndTTmWiOS-M) you must additionally check the `is_member` flag.
* left — “they flew away, but promised to come back”, i.e., the user left the group, 
but can return if desired. And at the time of leaving, they were not in a `restricted` state.
* banned — the user is banned and cannot return on their own until they are 
[unbanned](https://core.telegram.org/bots/api#unbanchatmember).

With this information at hand, it’s not hard to guess that the event “bot was added to a group” is a transition from 
the set of states `{banned, left, restricted(is_member=False)}` 
to the set `{restricted(is_member=True), member, administrator}`. Such a transition in English is called a transition, and 
in **aiogram 3.x** there are already templates for this. 

Option #1: simply list all states before and after:

```python
# Don’t forget the imports:
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, KICKED, LEFT, MEMBER, \
    RESTRICTED, ADMINISTRATOR, CREATOR

@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=
        (KICKED | LEFT | -RESTRICTED)
        >>
        (+RESTRICTED | MEMBER | ADMINISTRATOR | CREATOR)
    )
)
```

The vertical bar means “or”, the bitwise operator “>>” shows the direction of the transition, 
and the “plus” and “minus” symbols around RESTRICTED relate to the `is_member` flag (plus - True, minus - False).

But the aiogram developer went further and wrapped these two sets in separate states `IS_NOT_MEMBER` and `IS_MEMBER` 
respectively. Let’s simplify our code as option #2:

```python
# Slightly different imports
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER

@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=
        IS_NOT_MEMBER >> IS_MEMBER
    )
)
```

But since, I repeat, such a transition is quite common in bots, the developer went _even further_ and 
wrapped such a transition in the `JOIN_TRANSITION` variable, getting option #3:

```python
# Even fewer imports
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, JOIN_TRANSITION

@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=JOIN_TRANSITION
    )
)
```

I strongly recommend checking out all the state sets and transitions 
[in the documentation](https://docs.aiogram.dev/en/dev-3.x/dispatcher/filters/chat_member_updated.html) 
to make your code cleaner.

Now let’s create another router with two handlers that react to adding the bot 
to a group or supergroup as an administrator and regular member. 
When added, we’ll send a summary of where the bot was added to the chat:

```python title=”handlers/bot_in_group.py”
from aiogram import F, Router
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER, ADMINISTRATOR
from aiogram.types import ChatMemberUpdated

router = Router()
router.my_chat_member.filter(F.chat.type.in_({“group”, “supergroup”}))

chats_variants = {
    “group”: “group”,
    “supergroup”: “supergroup”
}


# Couldn’t reproduce the case of adding the bot as Restricted,
# so there will be no example with it


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> ADMINISTRATOR
    )
)
async def bot_added_as_admin(event: ChatMemberUpdated):
    # Simplest case: bot added as admin.
    # We can easily send a message
    await event.answer(
        text=f”Hello! Thank you for adding me to “
             f’the {chats_variants[event.chat.type]} “{event.chat.title}” ‘
             f”as an administrator. Chat ID: {event.chat.id}”
    )


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> MEMBER
    )
)
async def bot_added_as_member(event: ChatMemberUpdated, bot: Bot):
    # More complex case: bot added as regular member.
    # But there may be no write permission, so let’s check in advance.
    chat_info = await bot.get_chat(event.chat.id)
    if chat_info.permissions.can_send_messages:
        await event.answer(
            text=f”Hello! Thank you for adding me to “
                 f’the {chats_variants[event.chat.type]} “{event.chat.title}” ‘
                 f”as a regular member. Chat ID: {event.chat.id}”
        )
    else:
        print(“Log this situation somehow”)
```

But, as always, there’s a nuance, and to see it, you need to add the bot to a group, 
and then convert it to a supergroup. For clarity, I created a group 
with my bot [@my_id_bot](https://t.me/my_id_bot), and then added a test bot with the code described above. 
Pay attention to the screenshot:

![converting a group to a supergroup](../images/ru/special-updates/group_supergroup.png)

Oh, why did the bot react as if it was just added, when nothing seems to have changed. 
In fact, converting a group to a supergroup looks to the bot like adding to a new chat. Fortunately, in 
this case, the bot also receives a Message with non-empty 
`migrate_from_chat_id` and `migrate_to_chat_id` fields. And then it’s simple: when the `my_chat_member` event 
triggers on adding to a supergroup, check that there haven’t been any messages 
with a non-empty `migrate_to_chat_id` field recently (say, in the last couple of seconds).

The solution practically fully repeats the examples described above and moreover, it’s implemented in my [@my_id_bot](https://t.me/my_id_bot): 
[like this](https://github.com/MasterGroosha/my-id-bot/blob/17fa99945dd4eb186a7f2a200567829641edbe74/bot/handlers/add_or_migrate.py)
(stars on GitHub are always welcome)

!!! info “Groups and Supergroups”
    Contrary to popular misconception, regular groups still exist and have no intention of disappearing. The official 
    Telegram clients initially create a regular group, which implicitly converts to a supergroup when some event occurs. 
    And there are serious suspicions that such behavior won’t change in the coming years, 
    especially given that regular (non-premium) accounts have a limit of 500 supergroups and channels combined.

    During conversion, in addition to the chat ID change, there are also some side effects, so often the simplest thing 
    to do is convert the group to a supergroup immediately after creation, get the final ID, and not worry about it. 
    The complete list of actions that lead to converting a group to a supergroup can be seen here: 
    [https://t.me/tgbeta/3424](https://t.me/tgbeta/3424).


## chat_member Update {: id=”chat-member” }

The next special type of updates `chat_member` is tricky. The thing is, it’s not sent by Telegram by default, 
and for the Bot API to send it, you need to pass a list of desired event types when calling **getUpdates** or **setWebhook**. 
For example:

```python
# imports here

async def main():
    # code here
    dp = Dispatcher()
    bot = Bot(“token”)
    await dp.start_polling(
        bot, 
        allowed_updates=[“message”, “inline_query”, “chat_member”]
    )
```

Then, after starting the bot, Telegram will start sending the three specified types of events, but without all the others.

The aiogram developers approached this topic elegantly: if you don’t explicitly specify `allowed_updates`, then 
the framework will recursively go through all routers, starting with the dispatcher, look at the handlers, and automatically 
collect the list of desired updates to receive. Want to override this behavior? Pass `allowed_updates` explicitly.

!!! tip “Why am I not receiving the <XXX> update???”
    In specialized chats, people regularly ask: “My code doesn’t work, doesn’t respond to the event, why?”

    The first thing you should do is make sure the required update is being received by the bot at all. In other words, check 
    what `allowed_updates` was used when polling/webhooks were last called. The easiest way to do this is right in the browser:

    1. Take the bot token, let’s call it AAAAA
    2. Form a URL like `https://api.telegram.org/botAAAAA/getWebhookInfo`
    3. Go to it

    Then carefully study the JSON in the response. If the `allowed_updates` key is present, make sure the desired 
    update type is in the list. If the key is missing, this is equivalent to “everything comes except `chat_member`”

### Actualizing the Admin List in Groups {: id=”actualizing-admins” }

A common problem for moderator bots: how to impose access rights checks on called commands. 
For example, how to make only group administrators able to ban participants with the /ban command. 

The first and naive idea is to call getChatMember each time to determine the calling user’s status in the group. 
The second idea is to cache this knowledge for a short time. 
The third and more correct idea is to get the admin list when the bot starts, 
and then listen to chat_member updates about changes in their composition and edit the list yourself. 
Did the bot restart? No problem, we get the current list again and work with it.

Let’s write a router in which we’ll monitor changes in the admin composition and update the externally passed list 
(more precisely, in Python terms, it will be a set):

```python title=”handlers/admin_changes_in_group.py”
from aiogram import F, Router
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, KICKED, LEFT, \
    RESTRICTED, MEMBER, ADMINISTRATOR, CREATOR
from aiogram.types import ChatMemberUpdated

from config_reader import config

router = Router()
router.chat_member.filter(F.chat.id == config.main_chat_id)


@router.chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=
        (KICKED | LEFT | RESTRICTED | MEMBER)
        >>
        (ADMINISTRATOR | CREATOR)
    )
)
async def admin_promoted(event: ChatMemberUpdated, admins: set[int]):
    admins.add(event.new_chat_member.user.id)
    await event.answer(
        f”{event.new_chat_member.user.first_name} “
        f”was promoted to Administrator!”
    )


@router.chat_member(
    ChatMemberUpdatedFilter(
        # Pay attention to the arrow direction
        # Or you could swap the objects in the parentheses
        member_status_changed=
        (KICKED | LEFT | RESTRICTED | MEMBER)
        <<
        (ADMINISTRATOR | CREATOR)
    )
)
async def admin_demoted(event: ChatMemberUpdated, admins: set[int]):
    admins.discard(event.new_chat_member.user.id)
    await event.answer(
        f”{event.new_chat_member.user.first_name} “
        f”was demoted to regular user!”
    )
```

Now let’s write another router with a handler for the `/ban` command. In the handler itself, we’ll check if the calling 
user’s ID is in the `admins` set and allow or disallow the ban based on this:

```python title=”handlers/events_in_group.py”
from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.types import Message

router = Router()

# Actually, you can hang a custom filter on the router
# that checks if the calling user’s ID is in the admins set.
# Then all handlers in the router will automatically be called
# only for people from admins, this will reduce code and avoid unnecessary if
# But for the example, we’ll do it through if-else, to make it clearer


@router.message(Command(“ban”), F.reply_to_message)
async def cmd_ban(message: Message, admins: set[int]):
    if message.from_user.id not in admins:
        await message.answer(
            “You don’t have enough rights to perform this action”
        )
    else:
        await message.chat.ban(
            user_id=message.reply_to_message.from_user.id
        )
        await message.answer(“Violator has been banned”)
```

It remains to register the routers in the main file and load the admin list at startup. Here’s the full 
contents, along with all the previous changes.

```python title=”bot.py”
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config_reader import config
from handlers import in_pm, bot_in_group, admin_changes_in_group, events_in_group


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=”%(asctime)s - %(levelname)s - %(name)s - %(message)s”,
    )

    dp = Dispatcher()
    bot = Bot(
        config.bot_token.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    dp.include_routers(
        in_pm.router, events_in_group.router,
        bot_in_group.router, admin_changes_in_group.router
    )

    # Loading the admin list
    admins = await bot.get_chat_administrators(config.main_chat_id)
    admin_ids = {admin.user.id for admin in admins}

    await dp.start_polling(bot, admins=admin_ids)


if __name__ == ‘__main__’:
    asyncio.run(main())
```

Now let’s see what we ended up with. Try calling the `/ban` command as a non-admin:

![User doesn’t have enough rights](../images/ru/special-updates/ban_insufficient_rights.png)

Go to the group settings and make Arthur an administrator (the bot will see the change and report it in the chat):

![Now there’s enough rights](../images/ru/special-updates/ban_ok.png)

Revoke admin rights from our test subject and ask them to call the `/ban` command again:

![Not enough rights again](../images/ru/special-updates/ban_insufficient_again.png)

Now you know how to work with these “invisible” updates, hooray! Finally, I recommend checking out 
[one more demonstration bot](https://github.com/MasterGroosha/telegram-report-bot), which 
uses some of the tricks described above.

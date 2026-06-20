---
title: Getting Started with aiogram
description: Getting Started with aiogram
---

# Getting Started with aiogram {: id="start" }

!!! info ""
    aiogram version used: 3.27.0

!!! warning "Some details are intentionally simplified!"
    I am convinced that along with theory, there should also be practice. To make it easier for readers to replicate the examples described below, 
    I had to use approaches suitable only for local development and learning.

    Or sometimes data storage structures located exclusively in memory (dictionaries, lists...) will be used. In reality, such objects are undesirable, since stopping 
    the bot will lead to irreversible data loss.

    Also, polling was chosen as the mechanism for receiving updates from Telegram, since it is guaranteed to work 
    in the vast majority of environments and suits almost all developers.

    **It is important to remember that my goal is to explain specifically how to work with the Telegram Bot API using 
    aiogram, not to teach all of Computer Science in its entirety.**

## Terminology {: id="glossary" }

Let's introduce some terms so we can be on the same page moving forward:

* DM — direct messages, in the context of a bot this is a one-on-one conversation with a user, not a group/channel.
* Chat — a general term for DMs, groups, supergroups, and channels.
* Update — any event from [this list](https://core.telegram.org/bots/api#update): 
messages, message edits, callbacks, inline queries, payments, adding bots to groups, etc.
* Handler — an asynchronous function that receives the next update from the dispatcher/router 
and processes it.
* Dispatcher — an object responsible for receiving updates from Telegram and subsequently selecting a handler 
to process the received update.
* Router — similar to the dispatcher, but responsible for a subset of handlers.
* Filter — an expression that usually returns True or False and affects whether a handler will be called or not.
* Middleware — a layer that is inserted into the processing of updates.

## Installation {: id="installation" }

At the time of writing this chapter (2026), the popular package manager for Python applications 
is [uv](https://docs.astral.sh/uv/), and demonstration projects on GitHub will gradually be migrated to it.

If you downloaded an existing project that already uses `uv`, all you need to do is run `uv sync`, 
the package manager will automatically download the required Python version if necessary and install all packages 
from `pyproject.toml`. However, if you are creating a project from scratch, execute the following commands in sequence:

```bash
uv init --python 3.14
uv add aiogram
uv run python -c "import aiogram"
```

For the Python version, you can specify any current version that has received at least one or two patch updates 
(for example, `3.14.2` or `3.15.1`). If there are no errors in the terminal after `uv run python -c "import aiogram"`, 
then you have installed everything correctly.


## First Bot {: id="hello-world" }

!!! warning "Asynchronous programming in Python"
    aiogram is an asynchronous library, so without experience working with asyncio it will be difficult.  
    A great tutorial on asynchronicity is available 
    [on the Python website](https://docs.python.org/3/library/asyncio-task.html).

For educational purposes, let's write a simple single-file bot to understand what aiogram is and how user interaction with the bot works. I should warn you upfront: keeping all code in one file quickly becomes a bad idea, but it works well in two cases: demo code and one-off bots, for example, to quickly check something. In any case, later in this chapter we will write a more advanced bot with proper file structure.

Our first bot will have just one handler: it will send the legendary "Hello world!" in response to any message. What exactly is a handler? It's an **asynchronous function** that receives an object of some event from Telegram (a message, a callback, etc.) and does something with that event. 
For aiogram to know that a function declares itself as an event handler, it must be registered, 
i.e., attached to aiogram somehow. But this attachment doesn't happen to the framework itself, but to a specific object in it – the **dispatcher**.

Create a file `single_file_bot.py` in your project directory with the following content:

```python title="single_file_bot.py"
import asyncio                           # [1]
from os import getenv                    # [1]

from aiogram import Bot, Dispatcher      # [1]
from aiogram.types import Message        # [1]

dp = Dispatcher()                        # [2]


@dp.message()                            # [3]
async def any_message(                   # [4]
        message: Message,                # [5]
):
    await message.answer("Hello world!") # [6]


async def main():
    token = getenv("BOT_TOKEN")          # [7]
    if not token:                        # [7]
        error = "No token provided"      # [7]
        raise ValueError(error)          # [7]
    bot = Bot(token=token)               # [8]

    print("Starting bot...")
    try:
        await dp.start_polling(bot)      # [9]
    finally:
        print("Bot stopped")


if __name__ == '__main__':
    asyncio.run(main())
```

Very compact code, and almost every line has meaning. The numbers in the comments indicate:

1. Imports. `asyncio` is required for execution, `getenv` allows you to read the token from environment variables. From aiogram imports: the first two (`Bot`, `Dispatcher`) are mandatory, the last one (`Message`) is needed only for type hints and IDE suggestions.
I highly recommend not neglecting type hints, it simplifies both writing and reading code and maintaining it.
2. Creating a dispatcher object. In this example, it's created at the module level, since a handler will be registered with it later.
3. A decorator that reads as "the function under this decorator is registered in the router to handle 
updates of type `Message` (the update lies in the `message` field of the `Update` class that comes from Telegram)".
4. Declaration of a function that will handle the `Message` type update.
5. A parameter that will contain the update body when the function is called (in this case, of type `Message`).
Handler functions **always** have at least one parameter (possibly more), and the type of this parameter's value depends on what type 
the function is registered for.
6. The handler's business logic. In this case, a message is sent to the same chat where the original event came from. We'll talk more about sending messages in the next chapter.
7. Reading the token from the `BOT_TOKEN` environment variable. If the variable is not set or contains an empty value, raise an error.
8. Creating a bot object with the previously obtained token.
9. Starting the bot in polling mode.

Run the bot by passing the real token obtained from `@BotFather` as an environment variable. You should see a startup message and the bot will respond to any message with "Hello world!":

```
$ BOT_TOKEN=1234567890:AaBbCcDdEeFfGrOoShAHhIiJjKkLlMmNnOo uv run single_file_bot.py
```

![Bot is working](../images/ru/quickstart/l01_1_new_dark.png#only-dark)
![Bot is working](../images/ru/quickstart/l01_1_new_light.png#only-light)

Congratulations: your first bot is ready! But as mentioned earlier, keeping all code in one file is not the best idea. So let's give ourselves a quick pat on the back for hello world and do it properly.

## Bot Skeleton {: id="file-structure" }

Over the years of working with the Telegram Bot API, I have developed a certain style of writing code in general and Telegram bots 
in particular, so the code in the chapters will be based on it. It's important to note that there is no ideal approach 
and you are free to organize your source code however you like, especially if this code won't be shown to anyone else.

For example, here's what a simplified file structure of my typical bot looks like:

```
.
├── README.md
├── alembic
│   └── <migration files>
├── alembic.ini
├── bot
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py
│   ├── db
│   │   └── <various files>
│   ├── handlers
│   │   ├── __init__.py
│   │   └── <various files>
│   ├── i18n
│   │   └── <various files>
│   ├── logging_config.py
│   └── middlewares
│       ├── __init__.py
│       └── <various files>
├── settings.example.toml
├── settings.toml
├── pyproject.toml
└── uv.lock
```

Above I've omitted various utility files and directories, for example, `Makefile`, a `deploy` directory with scripts 
for deploying the application to a server, tests and so on. Let's talk about what remains in the structure:

`config.py`: this is where the bot's configuration is described: tokens, DSN for database connections, log parameters, 
various external API keys, etc. In recent years, I prefer the TOML format for storing settings, 
it doesn't have the "indentation disease" inherent to YAML, data is easy to group by sections, 
and the format itself is considered "native" in Python 3.12+. However, since open-source projects of mine periodically receive 
comments from users asking how to run my bots using only environment variables for configuration, 
I now add a fallback by supporting env vars in my code. For example, if `settings.toml` contains:

```toml
[bot]
token = "1234567890:AaBbCcDdEeFfGrOoShAHhIiJjKkLlMmNnOo"
```

Then you can specify the same value without a TOML file, but through environment variables like this:

```
# double underscore as delimiter is set in config.py
BOT__TOKEN=1234567890:AaBbCcDdEeFfGrOoShAHhIiJjKkLlMmNnOo
```

`logging_config.py`: I have long used [structlog](https://www.structlog.org/en/stable/) for logging, because 
JSON logs are very convenient and allow values to be parsed by automated tools.
In my bots, I collect both logs and various metrics with exceptions, all of which are then sent to a separate system, 
but that's not what we're talking about now. I don't use OpenTelemetry directly, because in my paradigm an application should not know who is observing it or how, it should only "spit out" logs and metrics, and whoever picks them up doesn't really matter.

`handlers`: a directory where handlers are located, i.e., event processors from Telegram. Some handlers are grouped into one file, while others are so complex that they deserve their own `py` file. In `__init__.py`, I usually import all nearby handler files and put a `get_routers()` function that collects the router hierarchy. An example from one of my projects:

```python
from aiogram import F, Router

from . import start, errors, admin


def get_routers(
        admins_list: list[int],
) -> list[Router]:

    admin.router.message.filter(F.from_user.id.in_(admins_list))

    return [
        start.router,
        errors.router,
        admin.router,
    ]
```

Similarly, the `filters` and `middlewares` directories are structured, if the project needs filters and middlewares respectively.

`i18n`: a directory for different locales (i18n is short for internationalization). Here are translations of various bot strings 
into different languages and a wrapper for working with strings via [Mozilla Fluent](https://projectfluent.org/python-fluent/).

`settings.toml` and `settings.example.toml`: a file with real ("production") settings and a file with placeholders. The first one always stays in `.gitignore` and never leaves the computer where it was created, the second one is always committed to git. An example of such a template file from one of my projects:

```toml
[bot]
token = "1234567890:AaBbCcDdEeFfGrOoShALlMmNnOoPpQqRrSs"
max_quote_len = 2000
admins = [1234567]

[logs]
project_name = "some_bot"
show_datetime = true
datetime_format = "%Y-%m-%d %H:%M:%S"
show_debug_logs = true
time_in_utc = false
use_colors_in_console = false
renderer = "json"
allow_third_party_logs = true
```

`__main__.py`: the entry point. Here all configuration data is read, the bot is set up, database connections are made, 
other connectors are initialized, and polling is started or webhooks are configured.
And the bot is easily launched as `uv run -m bot` (without `uv` it would be `python -m bot` in an activated Venv).

Don't be afraid of such a complex description, in reality everything looks quite simple, and some pieces of code 
can be safely copied from project to project unchanged. Now let's prepare the skeleton of your first bot.

In the directory where you previously initialized the `uv` project, create the following structure with empty files (don't touch `pyproject.toml` and `uv.lock`):

```
bot
├── __init__.py
├── __main__.py
├── config.py
├── handlers
│   ├── __init__.py
│   └── start.py
└──logging_config.py
settings.example.toml
settings.toml
pyproject.toml
uv.lock
```

Additionally, install a couple of libraries that will be useful for working with configuration and logs:

```shell
uv add pydantic-settings structlog
```

If the directory is part of a git repository, be sure to add `settings.toml` to `.gitignore`. Get the contents of the 
`config.py` and `logging_config.py` files from the 
[01_quickstart](https://github.com/MasterGroosha/aiogram-3-guide/tree/master/code/01_quickstart) directory from the git repository 
for this book. Next, let's talk about the business logic itself.


## Second Bot {: id="second-bot" }

Let's set a goal for this chapter: write a bot that will respond "Hello!" to the `/start` command, 
and respond "I don't understand you" to any other input. Let's start with the broader approach, i.e., with a handler for "any message".

When the dispatcher receives an event from Telegram, it faces the task of selecting which of the registered handlers will process it. 
To do this, the dispatcher checks each handler in turn against some criterion – a **filter**.
If the condition in the filter returns True, the dispatcher passes the event (update) to the handler and that's it.
If the filter returns False, the dispatcher tries the next handler and so on, until the handlers run out.
So we make the following important conclusions:

!!! info ""
    • A handler ensures processing of an event from Telegram.  
    • A handler must be registered with the dispatcher.  
    • The dispatcher selects handlers in sequence, checking the filters of each handler.  
    • The dispatcher passes the update to the first handler whose filter returns True. If there are none, the update is not passed to anyone.

Since the dispatcher exists in a single instance, passing it from file to file for handler registration 
can be cumbersome and easily leads to circular dependencies: `file_1` imports code from `file_2` to register a handler, in `file_2` the dispatcher is imported from `file_1` -> circular import, error. To solve this problem, **routers** exist. A router is an object to which handlers are registered, and then the router is registered with the dispatcher. Moreover, you can set a filter not only on a handler, but also on a router; then if an update doesn't pass the router's filter, none of the router's handlers will be checked. From this we make a few more conclusions:

!!! info ""
    • Handlers are attached to the dispatcher explicitly (directly) or implicitly (through a router).  
    • A router combines one or more handlers.  
    • **The dispatcher is the root router**.  
    • Filters can be set on both handlers and the router as a whole.

Filters and another entity not described above – middlewares – will be discussed in more detail in later chapters.

Thus, when designing business logic, the programmer's task is to properly organize the hierarchy of handlers so that the desired handler is selected to process the update, not some other one.

Copy the following code into the file `bot/handlers/start.py`:

```python title="bot/handlers/start.py"
from aiogram import Router                       # [1]
from aiogram.types import Message                # [1]

router = Router(name="start")                    # [2]


@router.message()                                # [3]
async def any_message(
        message: Message,
) -> None:
    await message.answer("I don't understand you")
```

You see a very simple router with one handler. The numbers above indicate:

1. Imports. The first one (`Router`) is mandatory, the second one (`Message`) is needed only for type hints and IDE suggestions.
2. Creating a router instance. The optional `name` parameter sets the router's name, but it doesn't affect anything.
3. The decorator is now applied to the router instead of the dispatcher.

According to the specification, we should have two handlers, so let's add the second one. This time we can put everything in one router, since the code is small and both handlers are similar. But where to place the handler – above or below the `any_message` function? Right now the existing handler has no filters other than that it processes updates of type `Message`. Since our future handler for the `/start` command is more specialized, it makes sense to add it higher in the code so it's registered first. That way the dispatcher/router will first check if the handler matches the "this is the `/start` command" filter, and if not, check the next filter "any message", which will always return True.

Replace the entire contents of the `start.py` file with the following content:

```python title="bot/handlers/start.py"
from aiogram import Router
from aiogram.filters import CommandStart    # [1]
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart())             # [2]
async def cmd_start(
        message: Message,
) -> None:
    await message.answer("Hello!")


@router.message()                           # [3]
async def any_message(
        message: Message,
) -> None:
    await message.answer("I don't understand you")
```

Let's note the following:

1. The `CommandStart` filter is imported. It, as the name suggests, will return True if the message is the `/start` command. For any other commands, there's a general `Command` filter, which you'll see in later chapters.
2. The aforementioned filter is attached to the `cmd_start()` handler.
3. The old handler remains unchanged: there's no need to create a separate "everything that's not the `/start` command" filter for `any_message()`, since when the `cmd_start()` handler is triggered, other handlers won't be checked.

A small tangent: occasionally there are situations where a filter is dynamic, i.e., its specific 
parameters are unknown until the bot starts. In such cases, handlers should be registered not through a decorator, 
but through the router's or dispatcher's `register()` method. Then the `start.py` file would look slightly different:

```python title="bot/handlers/start.py"
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="start")


async def cmd_start(
        message: Message,
) -> None:
    await message.answer("Hello!")


async def any_message(
        message: Message,
) -> None:
    await message.answer("I don't understand you")


# Somewhere below in this file, possibly inside some function:
router.message.register(cmd_start, CommandStart())
router.message.register(any_message)
```

The router is created and the handlers are too. The handlers are attached to the router, but the router itself is not attached to anything yet. 
Let's start by assembling the router hierarchy (we have one, but still). To do this, write the following code in `bot/handlers/__init__.py`:

```python title="bot/handlers/__init__.py"
from aiogram import Router

from . import (
    start,
)


def get_routers() -> list[Router]:
    return [
        start.router,
    ]
```

Here everything is simple: we import all handler files from `bot/handlers` and return a list of routers in the required order, 
in exactly that order the dispatcher will check them. And what about the dispatcher itself? We'll create it in `bot/__main__.py` along with all other objects and bot startup:

```python title="bot/__main__.py"
import asyncio

import structlog
from structlog.typing import FilteringBoundLogger

from aiogram import Bot, Dispatcher
from bot.config import Settings
from bot.handlers import get_routers
from bot.logging_config import get_structlog_config

logger: FilteringBoundLogger = structlog.get_logger()

async def main() -> None:
    # Reading configuration (toml file or env vars – doesn't matter)
    settings = Settings()
    # Configuring the logger
    structlog.configure(**get_structlog_config(settings.logs))

    # Creating a bot object. The mandatory token argument is read
    # from the configuration. Since the token is marked as SecretStr, it's necessary
    # to additionally call get_secret_value().
    bot = Bot(
        token=settings.bot.token.get_secret_value(),
    )

    # Creating a dispatcher object and attaching routers
    dp = Dispatcher()
    # A small hack: include_routers() accepts an arbitrary number of arguments
    # get_routers() returns a list: [A, B, C,...]
    # and this list will be passed as a set of arguments:
    # include_routers(A, B, C,...)
    dp.include_routers(*get_routers())

    # Starting the bot in polling mode
    await logger.ainfo("Starting polling...")
    try:
        await dp.start_polling(bot)
    finally:
        await logger.ainfo("Bot stopped")


asyncio.run(main())
```

Comments are provided directly in the code above, we won't dwell on them separately for now. Update the `settings.example.toml` file:

```toml
[bot]
token = "1234567890:AaBbCcDdEeFfGrOoShAHhIiJjKkLlMmNnOo"


[logs]
project_name = "hello_world"
show_datetime = true
datetime_format = "%Y-%m-%d %H:%M:%S"
show_debug_logs = false
time_in_utc = false
use_colors_in_console = true
renderer = "console"  # "console" or "json"
allow_third_party_logs = true
```

And in `settings.toml` copy the code above, but replace the token with your real one obtained from `@BotFather`. Now confidently launch the bot:

```
$ uv run -m bot              
2026-05-07 14:38:49 [info] Starting polling...            project_name=hello_world
2026-05-07 14:38:49 [info] Start polling                  project_name=hello_world
2026-05-07 14:38:49 [info] Run polling for bot @bot id=1234567890 - 'test_bot' project_name=hello_world
```

Write something to the bot to make sure it works correctly:

![Bot is working](../images/ru/quickstart/l01_2_new_dark.png#only-dark)
![Bot is working](../images/ru/quickstart/l01_2_new_light.png#only-light)

And congratulations again! You've written a second bot on aiogram and laid the foundation on which in the following chapters we will explore other capabilities of the framework and Telegram Bot API.

---
title: aiogram 入门
description: aiogram 入门
---

# aiogram 入门 {: id="start" }

!!! info ""
    使用的 aiogram 版本: 3.27.0

!!! warning "一些细节被有意简化了!"
    我相信除了理论之外，还应该有实践。为了让读者更容易重复后面描述的示例，
    我不得不采用只适合本地开发和学习的方法。

    或者有时数据存储会使用仅位于内存中的数据结构（字典、列表等）。
    实际上不建议使用这样的对象，因为停止机器人会导致数据永久丢失。

    此外，获取来自 Telegram 的更新的机制被选为轮询（polling），
    因为它保证在绝大多数环境中都能工作，并且适用于几乎所有开发人员。

    **重要的是要记住，我的目标是解释如何使用 aiogram 与 Telegram Bot API 交互，
    而不是解释计算机科学的全部内容。**

## 术语 {: id="glossary" }

让我们引入一些术语，以便以后不会混淆：

* LS（私聊）— 私人消息，在机器人的背景下是与用户的一对一对话，而不是群组/频道。
* 聊天 — 私聊、群组、超级群组和频道的通用名称。
* 更新 — [此列表](https://core.telegram.org/bots/api#update)中的任何事件：
消息、消息编辑、回调、内联查询、支付、将机器人添加到群组等。
* 处理程序 — 异步函数，从调度程序/路由器接收下一个更新并处理它。
* 调度程序 — 负责从 Telegram 获取更新，然后为收到的更新选择处理程序的对象。
* 路由器 — 类似于调度程序，但负责处理程序子集。
* 过滤器 — 通常返回 True 或 False 的表达式，影响处理程序是否被调用。
* 中间件 — 插入更新处理中的中间层。

## 安装 {: id="installation" }

在本章编写时（2026 年），流行的 Python 应用程序包管理器是 [uv](https://docs.astral.sh/uv/)。
GitHub 上的演示项目将逐步迁移到它。

如果您已下载使用 `uv` 的现有项目，所需要做的就是执行 `uv sync`，
包管理器将自动下载所需的 Python 版本（如果需要）并从 `pyproject.toml` 安装所有包。
但是，如果您从头开始创建项目，请依次执行以下命令：

```bash
uv init --python 3.14
uv add aiogram
uv run python -c "import aiogram"
```

您可以指定任何最新的并获得至少一两个补丁修复的 Python 版本
（例如，`3.14.2` 或 `3.15.1`）。如果在执行 `uv run python -c "import aiogram"` 后终端中没有错误，
则表示您安装正确。


## 第一个机器人 {: id="hello-world" }

!!! warning "Python 中的异步编程"
    aiogram 是一个异步库，所以在没有 asyncio 经验的情况下会很困难。
    有一个很好的异步教程可在 [Python 网站](https://docs.python.org/3/library/asyncio-task.html) 上获得。

出于教学目的，我们将编写最简单的单文件机器人，以了解 aiogram 是什么以及用户与机器人如何交互。
我会提前警告：将所有代码保存在一个文件中很快就会成为一个坏主意，但适合两种情况：
演示代码和一次性机器人，例如，快速检查某些内容。
无论如何，在本章稍后，我们将编写一个更高级的机器人，具有正常的文件结构。

在我们的第一个机器人中，只有一个处理程序：它将对任何消息回复传奇的 "Hello world!"。
那么处理程序（处理函数）到底是什么？
这是一个**异步函数**，它接收来自 Telegram 的某种事件对象（消息、回调等）并对该事件执行某些操作。
为了让 aiogram 知道这样的函数声称自己是事件处理程序，必须注册它，
即以某种方式将其绑定到 aiogram。但这种绑定不是针对框架本身，
而是针对其中的一个单独对象 — **调度程序**。

在项目目录中创建一个包含以下内容的 `single_file_bot.py` 文件：

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

这是非常紧凑的代码，几乎每一行都有意义。注释中的数字表示：

1. 导入。`asyncio` 对于运行是必需的，`getenv` 允许从环境变量读取令牌。
从 aiogram 的导入：前两个（`Bot`、`Dispatcher`）是必需的，最后一个（`Message`）仅用于类型注解和 IDE 提示。
我强烈建议不要忽视类型注解，这简化了代码的编写、阅读和维护。
2. 创建调度程序对象。在此示例中，它是在模块级别创建的，因为处理程序将在以后注册到它。
3. 装饰器，读作"此装饰器下的函数在 `router` 路由器中注册，以处理 `Message` 类型的更新
（更新位于来自 Telegram 的更新类的 `Update` 类的 `message` 字段中）"。
4. 声明将处理 `Message` 类型更新的函数。
5. 参数，在函数调用时将包含更新主体（在本例中为 `Message` 类型）。
处理程序**始终**至少有一个参数（可以有更多），该参数值的类型取决于函数注册的更新类型。
6. 处理程序的业务逻辑。在这个例子中，消息被发送到接收原始事件的同一聊天。我们将在下一章详细讨论消息发送。
7. 从 `BOT_TOKEN` 环境变量读取令牌。如果变量未设置或为空，则抛出错误。
8. 创建具有先前获得的令牌的机器人对象。
9. 在轮询模式下启动机器人。

通过将从 `@BotFather` 获得的实际令牌作为环境变量传递来运行机器人。您应该看到启动消息，
机器人将对任何消息回复文本 "Hello world!"：

```
$ BOT_TOKEN=1234567890:AaBbCcDdEeFfGrOoShAHhIiJjKkLlMmNnOo uv run single_file_bot.py
```

![机器人工作中](../images/ru/quickstart/l01_1_new_dark.png#only-dark)
![机器人工作中](../images/ru/quickstart/l01_1_new_light.png#only-light)

恭喜：您的第一个机器人已准备好！但是，如前所述，将所有代码保存在一个文件中不是一个好主意。
因此，让我们为 hello world 鼓掌，然后正确地做事。

## 机器人框架 {: id="file-structure" }

多年来与 Telegram Bot API 的合作让我养成了某种编写代码的风格，特别是 Telegram 机器人，
所以这些章节中的代码将基于它。这里需要注意的是，完美不存在，您可以自由地格式化您的源代码，
特别是如果您不打算向其他人展示这些代码。

例如，这是我的典型机器人的简化文件结构的样子：

```
.
├── README.md
├── alembic
│   └── <迁移文件>
├── alembic.ini
├── bot
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py
│   ├── db
│   │   └── <各种文件>
│   ├── handlers
│   │   ├── __init__.py
│   │   └── <各种文件>
│   ├── i18n
│   │   └── <各种文件>
│   ├── logging_config.py
│   └── middlewares
│       ├── __init__.py
│       └── <各种文件>
├── settings.example.toml
├── settings.toml
├── pyproject.toml
└── uv.lock
```

上面我省略了各种辅助文件和目录，例如 `Makefile`、用于在服务器上部署应用程序的脚本的 `deploy` 目录、
测试等。让我们讨论一下结构中留下的内容：

`config.py`：这里描述了机器人的配置：令牌、数据库连接的 DSN、日志参数、
各种外部 API 密钥等。近年来，我更喜欢 TOML 格式来存储设置，
它没有 YAML 固有的"缩进病"，数据很容易按部分分组，
格式本身在 Python 3.12+ 中被认为是"本地的"。但由于在我的开源项目中经常有评论者问如何运行我的机器人，
只有环境变量作为可配置参数，我现在在我的代码中添加了环回支持来支持环境变量。
例如，如果在 `settings.toml` 中写入：

```toml
[bot]
token = "1234567890:AaBbCcDdEeFfGrOoShAHhIiJjKkLlMmNnOo"
```

那么您可以通过环境变量指定相同的值而不使用 TOML 文件：

```
# 双下划线作为分隔符在 config.py 中设置
BOT__TOKEN=1234567890:AaBbCcDdEeFfGrOoShAHhIiJjKkLlMmNnOo
```

`logging_config.py`：我已经使用 [structlog](https://www.structlog.org/en/stable/) 进行日志记录很长时间了，
因为 JSON 日志非常方便，允许通过自动化工具解析值。
在我的机器人中，我收集日志和各种指标以及异常，然后将其发送到单独的系统，
但现在不是讨论它的时候。我不直接使用 OpenTelemetry，因为在我的范例中，应用程序不应该知道谁在监视它以及如何监视，
它应该只是"吐出"日志和指标，至于谁会收集它们，那不那么重要。

`handlers`：包含处理程序的目录，即来自 Telegram 的事件处理程序。某些处理程序分组到一个文件中，
某些处理程序非常复杂，以至于为它们分配一个单独的 `py` 文件。在 `__init__.py` 中，
我通常导入所有相邻的处理程序文件，并放置一个 `get_routers()` 函数，该函数收集路由器的层次结构。
来自我的一个项目的示例：

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

`filters` 和 `middlewares` 目录的结构类似，如果项目需要过滤器和中间件的话。

`i18n`：用于不同地区的目录（i18n 是国际化的缩写）。这里包含机器人各种字符串的翻译
各种语言和通过 [Mozilla Fluent](https://projectfluent.org/python-fluent/) 使用字符串的包装器。

`settings.toml` 和 `settings.example.toml`：实际（"生产"）设置文件和带有占位符的文件。
第一个始终在 `.gitignore` 中，永远不会离开创建它的计算机，第二个必须提交到 git。
来自我的一个项目的示例模板文件：

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

`__main__.py`：入口点。这是读取所有配置数据的地方，机器人已设置，
连接到数据库，初始化其他连接器以及通过轮询启动数据接收或设置 webhook。
而且机器人很容易以 `uv run -m bot` 的方式运行（没有 `uv` 的话在激活的 Venv 中是 `python -m bot`）。

不要害怕这样复杂的描述，实际上一切看起来相当简单，某些代码段可以安全地以不变的方式从一个项目复制到另一个项目。
现在让我们为您的第一个机器人准备框架。

在您之前初始化 `uv` 项目的目录中，创建以下结构和空文件（不要触及 `pyproject.toml` 和 `uv.lock`）：

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

另外安装几个有用的库来处理配置和日志：

```shell
uv add pydantic-settings structlog
```

如果目录是 git 存储库的一部分，请确保将 `settings.toml` 添加到 `.gitignore`。
`config.py` 和 `logging_config.py` 文件的内容来自本书 git 存储库的 
[01_quickstart](https://github.com/MasterGroosha/aiogram-3-guide/tree/master/code/01_quickstart) 目录。
接下来我们将直接讨论业务逻辑。


## 第二个机器人 {: id="second-bot" }

让我们为本章设定目标：编写一个机器人，对 `/start` 命令回复"你好！"，
对任何其他输入回复"我不理解你"。让我们从更广泛的开始，即"任何消息"处理程序。

当调度程序从 Telegram 接收事件时，它面临的任务是选择哪个已注册的处理程序来处理它。
为此，调度程序按顺序检查每个处理程序是否符合某个特定标志 — **过滤器**。
如果过滤器中的条件返回 True，则调度程序将事件（更新）传递给处理程序，就这样。
如果过滤器返回 False，调度程序将尝试下一个处理程序，依此类推，直到处理程序用完。
我们得出以下重要结论：

!!! info ""
    • 处理程序提供对来自 Telegram 的事件的处理。
    • 处理程序必须在调度程序中注册。
    • 调度程序按顺序选择处理程序，检查每个处理程序的过滤器。
    • 调度程序将更新传递给其过滤器返回 True 的第一个处理程序。如果没有，则更新不会传递给任何人。

由于调度程序以单个实例形式存在，将其从文件拖到文件以注册处理程序可能很困难，
并且容易导致循环依赖：`file_1` 导入 `file_2` 中的代码以注册处理程序，
在 `file_2` 中从 `file_1` 导入调度程序 -> 循环导入，错误。
为了解决这个问题，存在**路由器**。路由器是一个对象，处理程序在其中注册，
然后路由器在调度程序中注册。而且，您可以在路由器上设置过滤器，而不仅仅在处理程序上，
这样，如果更新没有通过路由器过滤器，则不会检查路由器的任何处理程序。从此我们可以得出几个更多的结论：

!!! info ""
    • 处理程序明确（直接）或隐式（通过路由器）绑定到调度程序。
    • 路由器将一个或多个处理程序组合在一起。
    • **调度程序是根路由器**。
    • 过滤器可以放在处理程序和整个路由器上。

过滤器及其他未在上面描述的实体 — 中间件 — 将在后续章节中更详细地讨论。

因此，在设计业务逻辑时，程序员的任务是正确组织处理程序的层次结构，
以便为更新选择所需的处理程序，而不是其他。

将以下代码复制到 `bot/handlers/start.py` 文件中：

```python title="bot/handlers/start.py"
from aiogram import Router                       # [1]
from aiogram.types import Message                # [1]

router = Router(name="start")                    # [2]


@router.message()                                # [3]
async def any_message(
        message: Message,
) -> None:
    await message.answer("Я тебя не понимаю")
```

在您面前是一个非常简单的路由器，只有一个处理程序。上面的数字表示：

1. 导入。第一个（`Router`）是必需的，第二个（`Message`）仅用于类型注解和 IDE 提示。
2. 创建路由器实例。可选参数 `name` 设置路由器的名称，但这不会影响任何内容。
3. 装饰器现在应用于路由器，而不是调度程序。

根据技术规范，我们应该有两个处理程序，现在让我们添加第二个。
这一次，我们可以将所有内容放在一个路由器中，因为代码不大，两个处理程序大致相似。
但处理程序应该放在哪里 — 在 `any_message` 函数的上方还是下方？
现在现有的处理程序没有任何过滤器，除了处理程序对 `Message` 类型的更新起作用这一事实。
由于我们未来的 `/start` 命令处理程序更专业化，有意义的是在代码中添加它前面，
以便它首先注册。在这种情况下，调度程序/路由器将首先检查处理程序与"这是 `/start` 命令"过滤器的对应关系，
如果不是，则检查下一个过滤器"任何消息"，这总是返回 True。

将 `start.py` 文件的全部内容替换为以下内容：

```python title="bot/handlers/start.py"
from aiogram import Router
from aiogram.filters import CommandStart    # [1]
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart())             # [2]
async def cmd_start(
        message: Message,
) -> None:
    await message.answer("Привет!")


@router.message()                           # [3]
async def any_message(
        message: Message,
) -> None:
    await message.answer("Я тебя не понимаю")
```

注意以下几点：

1. 添加了 `CommandStart` 过滤器的导入。正如其名称所示，如果消息是 `/start` 命令，它将返回 True。
对于任何其他命令，有一个通用的 `Command` 过滤器，您将在后面的章节中看到它。
2. 上述过滤器应用于 `cmd_start()` 处理程序。
3. 旧处理程序保持不变：不需要为 `any_message()` 创建单独的过滤器"不是 `/start` 命令的所有内容"，
因为当 `cmd_start()` 处理程序触发时，其他处理程序不会被检查。

一个小插曲：有时候过滤器是动态的，即它的具体参数在机器人启动之前是未知的。
在这种情况下，不应该通过装饰器注册处理程序，而应该通过路由器或调度程序的 `register()` 方法。
然后 `start.py` 文件看起来会有点不同：

```python title="bot/handlers/start.py"
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="start")


async def cmd_start(
        message: Message,
) -> None:
    await message.answer("Привет!")


async def any_message(
        message: Message,
) -> None:
    await message.answer("Я тебя не понимаю")


# 在这个文件的某个地方下面，可能在某个函数内部:
router.message.register(cmd_start, CommandStart())
router.message.register(any_message)
```

路由器已创建，处理程序也已创建。处理程序已绑定到路由器，但路由器本身尚未绑定到任何内容。
让我们首先收集路由器的层次结构（我们只有一个，但仍然需要）。为此，在 `bot/handlers/__init__.py` 中写入以下代码：

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

这里很简单：导入 `bot/handlers` 中所有带有处理程序的文件，并按所需顺序返回路由器列表，
调度程序将按照这个顺序检查它们。那么调度程序本身呢？我们将在 `bot/__main__.py` 中与所有其他对象和机器人启动一起创建它：

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
    # 读取配置（toml 文件或 env vars 无所谓）
    settings = Settings()
    # 配置日志记录器
    structlog.configure(**get_structlog_config(settings.logs))

    # 创建机器人对象。必需参数 token 从配置中读取。
    # 由于 token 被标记为 SecretStr，需要额外调用 get_secret_value()。
    bot = Bot(
        token=settings.bot.token.get_secret_value(),
    )

    # 创建调度程序对象并绑定路由器
    dp = Dispatcher()
    # 一个小技巧：include_routers() 接受任意数量的参数
    # get_routers() 返回列表：[A, B, C,...]
    # 这个列表将作为参数集传递：
    # include_routers(A, B, C,...)
    dp.include_routers(*get_routers())

    # 在轮询模式下启动机器人
    await logger.ainfo("Starting polling...")
    try:
        await dp.start_polling(bot)
    finally:
        await logger.ainfo("Bot stopped")


asyncio.run(main())
```

上面直接在代码中放置了注释，现在我们不会单独对其进行处理。更新 `settings.example.toml` 文件：

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

在 `settings.toml` 中复制上面的代码，但将令牌替换为您从 `@BotFather` 获得的真实令牌。现在可以安全地启动机器人：

```
$ uv run -m bot              
2026-05-07 14:38:49 [info] Starting polling...            project_name=hello_world
2026-05-07 14:38:49 [info] Start polling                  project_name=hello_world
2026-05-07 14:38:49 [info] Run polling for bot @bot id=1234567890 - 'test_bot' project_name=hello_world
```

给机器人写点东西来确保它工作正常：

![机器人工作中](../images/ru/quickstart/l01_2_new_dark.png#only-dark)
![机器人工作中](../images/ru/quickstart/l01_2_new_light.png#only-light)

再次祝贺！您已经用 aiogram 编写了第二个机器人，并奠定了在后续章节中考虑框架的其他功能和 Telegram Bot API 的基础。

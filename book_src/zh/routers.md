---
title: 路由器与结构
description: aiogram 路由与项目组织
---

# 路由器、多文件与机器人结构

!!! info ""
    使用的 aiogram 版本：3.7.0

在本章中，我们将熟悉 aiogram 3.x 的新功能——路由器，学习如何将代码分成单独的组件，以及形成机器人的基本结构，这在接下来的章节中和实际工作中都会派上用场。

## 应用程序入口点 {: id="entrypoint" }

戏剧始于衣帽间，而机器人始于入口点。让它是一个 `bot.py` 文件。在其中，我们将定义一个异步函数 `main()`，在其中创建必要的对象并启动轮询。哪些对象是必要的？首先，当然是机器人。可能有多个，但那是另一个故事了。其次，调度程序。它负责从 Telegram 接收事件并通过过滤器和中间件将它们分发给处理器。

```python title="bot.py"
import asyncio
from aiogram import Bot, Dispatcher


# 启动机器人
async def main():
    bot = Bot(token="TOKEN")
    dp = Dispatcher()

    # 启动机器人并跳过所有累积的传入
    # 是的，即使您使用轮询，此方法也可以调用
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

但要处理消息，这还不够，我们还需要处理器。我们想将它们放在其他文件中，以避免创建数千行的代码块。在前面的章节中，我们所有的处理器都附加到调度程序，但现在它在函数内部，我们肯定不想将其设为全局对象。
那我们该怎么办呢？这就是...出场的时候了

## 路由器 {: id="routers" }

让我们查阅[官方文档](https://docs.aiogram.dev/en/dev-3.x/dispatcher/router.html)
aiogram 3.x 并查看以下图像：

![多个路由器](https://docs.aiogram.dev/en/dev-3.x/_images/nested_routers_example.png)

我们看到什么？

1. 调度程序——根路由器。
2. 处理器附加到路由器。
3. 路由器可以嵌套，但它们之间只有单向连接。
4. 路由器的包含（因此检查）的顺序是明确确定的。

下面的图像显示了更新查找正确处理器执行的顺序：

![更新查找正确处理器的顺序](https://docs.aiogram.dev/en/dev-3.x/_images/update_propagation_flow.png)

让我们编写一个具有两个功能的简单机器人：

1. 如果机器人收到 `/start`，它应该发送一个问题和两个按钮，文本为"是"和"否"。
2. 如果机器人收到任何其他文本、贴纸或 gif，它应该回复消息类型的名称。

我们从键盘开始：在 `bot.py` 文件旁边创建一个 `keyboards` 目录，并在其中创建一个 `for_questions.py` 文件，并编写一个函数以获取一个简单的键盘，其中"是"和"否"按钮在一行中：

```python title="keyboards/for_questions.py"
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_yes_no_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Да")
    kb.button(text="Нет")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
```

没有什么复杂的，尤其是因为我们之前详细讨论了[键盘](buttons.md)。
现在在 `bot.py` 文件旁边创建另一个目录 `handlers`，并在其中创建一个文件 `questions.py`。

```python title="handlers/questions.py" hl_lines="7 9"
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.for_questions import get_yes_no_kb

router = Router()  # [1]

@router.message(Command("start"))  # [2]
async def cmd_start(message: Message):
    await message.answer(
        "Вы довольны своей работой?",
        reply_markup=get_yes_no_kb()
    )

@router.message(F.text.lower() == "да")
async def answer_yes(message: Message):
    await message.answer(
        "Это здорово!",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text.lower() == "нет")
async def answer_no(message: Message):
    await message.answer(
        "Жаль...",
        reply_markup=ReplyKeyboardRemove()
    )
```

让我们关注第 [1] 和 [2] 项。首先，我们在文件中创建了自己的模块级路由器，然后我们会将其附加到根路由器（调度程序）。其次，处理器已从本地路由器"分支出来"。

同样，我们创建第二个处理器文件 `different_types.py`，我们只需输出消息类型：

```python title="handlers/different_types.py"
from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text)
async def message_with_text(message: Message):
    await message.answer("Это текстовое сообщение!")

@router.message(F.sticker)
async def message_with_sticker(message: Message):
    await message.answer("Это стикер!")

@router.message(F.animation)
async def message_with_gif(message: Message):
    await message.answer("Это GIF!")

```

最后，让我们回到 `bot.py`，导入带有路由器的文件和处理器，并将它们连接到调度程序：

```python title="bot.py" hl_lines="3 11 12"
import asyncio
from aiogram import Bot, Dispatcher
from handlers import questions, different_types


# 启动机器人
async def main():
    bot = Bot(token="TOKEN")
    dp = Dispatcher()

    dp.include_routers(questions.router, different_types.router)

    # 逐行注册路由器的替代方法
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)

    # 启动机器人并跳过所有累积的传入
    # 是的，即使您使用轮询，此方法也可以调用
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

我们只是从 `handlers/` 目录导入文件并将这些文件中的路由器连接到调度程序。这里再次强调导入顺序的重要性！如果我们交换路由器的注册，那么对 `/start` 命令，机器人会以"这是一条文本消息！"作为回复，因为 `message_with_text()` 函数首先成功通过所有过滤器。但我们稍后会讨论过滤器本身，现在让我们考虑另一个问题。


## 总结 {: id="conclusion" }

我们成功地将机器人分成不同的文件，而不会影响其操作。近似的文件和目录树如下（此处故意省略了对示例不重要的某些文件）：

```
├── bot.py
├── handlers
│   ├── different_types.py
│   └── questions.py
├── keyboards
│   └── for_questions.py
```

进一步，我们将坚持这种结构，加上新增的用于过滤器、中间件、数据库工作等的目录。

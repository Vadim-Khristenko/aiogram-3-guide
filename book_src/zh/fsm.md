---
title: 有限状态机（FSM）
description: 有限状态机（FSM）
---

# 有限状态机（FSM） {: id="fsm-start" }

!!! info ""
    使用的 aiogram 版本：3.7.0

## 理论 {: id="theory" }

在本章中，我们将讨论机器人的另一个重要功能：**对话系统**。不幸的是，并非所有操作
都可以通过一条消息或命令完成。假设有一个交友机器人，在注册时需要指定名字、年龄并发送带脸部的照片。
当然可以要求用户在照片的标题中提供所有数据，但这对处理和重新输入请求不方便。

现在假设逐步输入数据，其中开始时机器人"启用"特定用户的等待特定信息的模式，
然后在每个步骤检查输入的数据，而通过 `/cancel` 命令停止等待下一步并
返回主模式。看一下下面的图表：

![由三个步骤组成的过程](../images/ru/fsm/l04_1.svg)

**绿色**箭头表示无错误地进行步骤的过程，**蓝色**箭头表示保持当前状态并
等待重新输入（例如，如果用户说他们 250 岁，应该重新请求年龄），**红色**
箭头显示由于 `/cancel` 命令或任何其他表示取消的命令而退出整个过程。

上面图表中的过程在算法理论中称为**有限状态机**（或 FSM — Finite State Machine）。更多信息可以在
[这里](https://tproger.ru/translations/finite-state-machines-theory-and-implementation/)阅读。

!!! info "对话构造器"
    在本章中练习 FSM 后，你肯定会感到为了获得复杂的分支操作链需要做很多事情。幸运的是，存在
    [**aiogram-dialog**](https://github.com/Tishka17/aiogram_dialog) 库
    来自 **Tishka17**，简化了与状态机的工作。

## 实践 {: id="practice" }

aiogram 中的有限状态机机制已经内置支持各种后端来存储
对话阶段之间的状态（虽然没有什么阻止你写自己的），而且除了状态本身之外，
你还可以存储任意数据，例如上面描述的名字和年龄供以后使用。
现有 FSM 存储列表可以在
[aiogram 仓库中找到](https://github.com/aiogram/aiogram/tree/dev-3.x/aiogram/fsm/storage)，
而在本章中我们将使用最简单的后端
[MemoryStorage](https://github.com/aiogram/aiogram/blob/dev-3.x/aiogram/fsm/storage/memory.py)，它
在 RAM 中存储所有数据。它非常适合示例，但**不建议**在实际项目中使用，因为 MemoryStorage
在没有保存到磁盘的情况下在 RAM 中存储所有数据。还值得注意的是，有限状态机不仅可以
与消息处理器（`message_handler`、`edited_message_handler`）一起使用，还可以
与回调和内联模式一起使用。

作为一个例子，我们将写一个在咖啡馆里模拟订购食物和饮料的程序。

### 创建步骤 {: id="define-states" }

在我们直接进行 FSM 之前，让我们快速描述一个简单的函数，它将生成
一个普通键盘，按钮排成一行，这在以后会很有用：

```python title="keyboards/simple_row.py"
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    创建一个带有一行按钮的回复键盘
    :param items: 按钮文本列表
    :return: 回复键盘对象
    """
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)
```

让我们考虑"订购"食物的步骤描述。创建文件 `handlers/ordering_food.py`，其中我们描述
食物列表及其大小（在现实生活中，这些信息可能从某个数据库动态加载）：

```python
# 这些值稍后将被替换到最终文本中，因此
# 形容词这看起来形式有点奇怪
available_food_names = ["Суши", "Спагетти", "Хачапури"]
available_food_sizes = ["Маленькую", "Среднюю", "Большую"]
```

现在让我们描述特定过程的所有可能"状态"（食物选择）。用语言可以这样描述：用户调用
命令 `/food`，机器人用请求选择菜品的消息回复并为该特定用户进入\*等待菜品选择\*状态。一旦
用户做出选择，机器人在这个状态中检查输入的正确性，然后决定要求重新输入（不改变状态）
或进入下一步\*等待选择份量\*。当用户在这里也输入正确的数据时，机器人显示
最终结果（订单内容）并重置状态。稍后在本章中，我们将学会如何在任何阶段使用
`/cancel` 命令强制重置状态。

### 处理第 1 步 {: id="step-1" }

好的，让我们直接进行状态描述。要存储状态，需要创建一个继承自 `StatesGroup` 的类，
在其中需要创建变量，给它们分配 `State` 类的实例：

```python
class OrderFood(StatesGroup):
    choosing_food_name = State()
    choosing_food_size = State()
```

让我们编写第一步的处理器，在用户没有设置任何状态时对命令 `/food` 做出反应：

```python hl_lines="4 10"
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

@router.message(StateFilter(None), Command("food"))
async def cmd_food(message: Message, state: FSMContext):
    await message.answer(
        text="Выберите блюдо:",
        reply_markup=make_row_keyboard(available_food_names)
    )
    # 为用户设置"选择名称"状态
    await state.set_state(OrderFood.choosing_food_name)
```

要使用 FSM 机制，需要将名为 `state` 的参数注入处理器中，其类型为 `FSMContext`。
在最后一行中，我们明确告诉机器人进入 `OrderFood` 组中的 `choosing_food_name` 状态。

!!! warning "与 aiogram 2.x 的区别"
    在 aiogram 2.x 中，缺少 state 过滤器意味着"仅在没有明确设置状态时"
    （换句话说，`state=None`）。在 aiogram 3.x 中，缺少过滤器意味着"在任何状态下"。
    提醒一下，"3"中使用了类似的方法来处理消息的内容类型。

接下来，让我们编写一个捕获我们列表中的菜品选项之一的处理器：

```python linenums="1"
@router.message(
    OrderFood.choosing_food_name, 
    F.text.in_(available_food_names)
)
async def food_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_food=message.text.lower())
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, выберите размер порции:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
    await state.set_state(OrderFood.choosing_food_size)
```

让我们更详细地查看处理器的某些元素。过滤器（第 2-3 行）说明，当且仅当用户处于
`OrderFood.choosing_food_name` 状态且消息文本与 `available_food_names` 列表中的其中一个元素匹配时，
下面的函数才会起作用。在第 6 行中，我们将数据（消息文本）写入 FSM 存储，这些数据对对
`(chat_id, user_id)` 对是唯一的（有一个注意事项，稍后再说）。最后，
在第 11 行中我们将用户转移到 `OrderFood.choosing_food_size` 状态。

如果用户决定自己输入东西，不使用键盘呢？在这种情况下，您需要告知用户有错误并再给他们一个机会。
非常经常，初学者 bot 开发者会在这一点上提出一个问题：
"如何让用户保持在同一状态中？"答案很简单：要让用户保持在当前状态中，
足够是不改变它，也就是说，按字面意思_什么都不做_。

让我们编写一个额外的处理器，它只在 `OrderFood.choosing_food_name` 状态上有过滤器，
但在文本上没有过滤器。如果将其放在 `food_chosen()` 函数下方，
那么你会得到"在 choosing_food_name 状态中响应，对所有文本，除了那些之前处理器捕获的文本"
（换句话说，"捕获所有不正确的选项"）。

```python
@router.message(OrderFood.choosing_food_name)
async def food_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого блюда.\n\n"
             "Пожалуйста, выберите одно из названий из списка ниже:",
        reply_markup=make_row_keyboard(available_food_names)
    )
```

### 处理第 2 步 {: id="step-2" }

第二个也是最后一个阶段是处理用户输入的份量。类似于前一个阶段，我们将制作两个处理器
（对于正确和不正确的答案），但在第一个中添加选择订单摘要信息：

```python hl_lines="3 9"
@router.message(OrderFood.choosing_food_size, F.text.in_(available_food_sizes))
async def food_size_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text=f"Вы выбрали {message.text.lower()} порцию {user_data['chosen_food']}.\n"
             f"Попробуйте теперь заказать напитки: /drinks",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@router.message(OrderFood.choosing_food_size)
async def food_size_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого размера порции.\n\n"
             "Пожалуйста, выберите один из вариантов из списка ниже:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
```

在第 3 行中调用 `get_data()` 返回特定用户在特定聊天中的存储对象。从它
\[存储\]中我们提取保存的菜品名称值并将其替换到消息中。`clear()` 方法的作用是
将用户返回到"空"状态并删除所有保存的数据。如果你只需要清除状态或只清除数据怎么办？
为此，让我们进入 aiogram 3.x 源代码中 `clear()` 函数的定义：

```python
class FSMContext:
    # 部分代码被跳过

    async def clear(self) -> None:
        await self.set_state(state=None)
        await self.set_data({})
```

现在你知道如何清除某个特定的东西了：）

选择饮料的步骤以完全相同的方式进行。尝试自己做或查看本章的源代码。

完整的食物订购处理器文件文本：

```python title="handlers/ordering_food.py"
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.simple_row import make_row_keyboard

router = Router()

# 这些值稍后将被替换到最终文本中，因此
# 形容词这看起来形式有点奇怪
available_food_names = ["Суши", "Спагетти", "Хачапури"]
available_food_sizes = ["Маленькую", "Среднюю", "Большую"]


class OrderFood(StatesGroup):
    choosing_food_name = State()
    choosing_food_size = State()


@router.message(Command("food"))
async def cmd_food(message: Message, state: FSMContext):
    await message.answer(
        text="Выберите блюдо:",
        reply_markup=make_row_keyboard(available_food_names)
    )
    # 为用户设置"选择名称"状态
    await state.set_state(OrderFood.choosing_food_name)

# 菜品选择阶段 #


@router.message(OrderFood.choosing_food_name, F.text.in_(available_food_names))
async def food_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_food=message.text.lower())
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, выберите размер порции:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
    await state.set_state(OrderFood.choosing_food_size)


# 总的来说，没什么阻止我们完全用字符串指定状态
# 如果出于某种原因你的状态名称在运行时生成，这可能会很有用（但为什么呢？）
@router.message(StateFilter("OrderFood:choosing_food_name"))
async def food_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого блюда.\n\n"
             "Пожалуйста, выберите одно из названий из списка ниже:",
        reply_markup=make_row_keyboard(available_food_names)
    )

# 选择份量阶段与显示订单摘要信息 #


@router.message(OrderFood.choosing_food_size, F.text.in_(available_food_sizes))
async def food_size_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text=f"Вы выбрали {message.text.lower()} порцию {user_data['chosen_food']}.\n"
             f"Попробуйте теперь заказать напитки: /drinks",
        reply_markup=ReplyKeyboardRemove()
    )
    # 重置用户的状态和保存的数据
    await state.clear()


@router.message(OrderFood.choosing_food_size)
async def food_size_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого размера порции.\n\n"
             "Пожалуйста, выберите один из вариантов из списка ниже:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
```

### 通用命令 {: id="common-commands" }

既然我们谈到了重置状态，让我们在文件 `handlers/common.py` 中实现 `/start` 命令的处理器和
"取消"操作。在前一种情况下，应该显示某种欢迎/参考文本，对于取消我们将编写
两个处理器：当用户不处于任何状态时，以及当用户处于某个状态时。

所有函数保证不存在状态和数据，如果有的话移除普通键盘：

```python title="handlers/common.py"
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Выберите, что хотите заказать: "
             "блюда (/food) или напитки (/drinks).",
        reply_markup=ReplyKeyboardRemove()
    )


# 不难看出，下面两个处理器可以轻松合并为一个，但为了完整性我们保留这样

# default_state 与 StateFilter(None) 相同
@router.message(StateFilter(None), Command(commands=["cancel"]))
@router.message(default_state, F.text.lower() == "отмена")
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    # 不需要重置状态，只删除数据
    await state.set_data({})
    await message.answer(
        text="Нечего отменять",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )

```

### bot.py 文件 {: id="entrypoint" }

最后，让我们考虑入口点 — `bot.py` 文件，具有所有导入和连接的路由器：

```python title="bot.py"
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# 可以从仓库中获取 config_reader.py 文件
# 示例 — 在第一章中
from config_reader import config
from handlers import common, ordering_food


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # 如果不指定 storage，默认仍然是 MemoryStorage
    # 但显式优于隐式 =]
    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(config.bot_token.get_secret_value())

    dp.include_router(common.router)
    dp.include_router(ordering_food.router)
    # 在这里导入你自己的饮料路由器

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
```

### 不同的 FSM 策略 {: id="strategies" }

Aiogram 3.x 在有限状态机机制中带来了一个不寻常但有趣的创新 — FSM 策略。它们允许
重新定义状态和数据对的形成逻辑。总共有五个策略，这些是：

* **USER_IN_CHAT** — 默认策略。每个用户在每个聊天中的状态和数据都不同。也就是说，一个用户
在不同的群组中会有不同的状态和数据，以及与机器人的私聊中的状态和数据。
* **CHAT** — 状态和数据对整个聊天都是通用的。在私聊中差异不明显，但在群组中所有参与者都会
有一个状态和通用数据。
* **GLOBAL_USER** — 在所有聊天中，同一用户会有相同的状态和数据。
* **USER_IN_TOPIC** — 用户可以根据
[超级群组论坛](https://telegram.org/blog/topics-in-groups-collectible-usernames#topics-in-groups)中的主题
有不同的状态。
* **CHAT_TOPIC** — 每个主题都有自己的状态，不分用户。

老实说，我想不到 **GLOBAL_USER** 的好用例，但是 **CHAT** 对于实现各种群组游戏的机器人可能很有用。
如果你知道有趣的应用，请在我们的聊天中告诉我们！

作为一个例子，让我们考虑食物订购机器人出于某种原因最终进入了一个群组并具有 **CHAT** 策略的情况。
而为了让这发生，需要在 `bot.py` 文件中做一点小改动：

```python
# 新的导入
from aiogram.fsm.strategy import FSMStrategy

async def main():
    # 这里是代码
    dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)
    # 这里也是代码
```

启动机器人后，让我们要求群组中的人与其互动：

![对于机器人来说，所有用户都是一样的](../images/ru/fsm/fsm_chat_strategy.png)

看起来很奇怪，不是吗？

现在，凭借关于有限状态机的知识，你可以毫无恐惧地写出带有对话系统的机器人。

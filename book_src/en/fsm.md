---
title: Finite State Machines (FSM)
description: Finite State Machines (FSM)
---

# Finite State Machines (FSM) {: id="fsm-start" }

!!! info ""
    aiogram version used: 3.7.0

## Theory {: id="theory" }

In this chapter, we'll discuss another important bot capability: the **dialog system**. Unfortunately, not every action in a bot can be completed in a single message or command. Imagine a dating bot where registration requires entering a name, age, and sending a face photo. You could ask the user to send everything in one caption with all the data, but that's inconvenient for validation and handling corrections.

Now imagine a step-by-step flow: the bot "activates" a state where it waits for specific information from a specific user. At each step, the input is validated. If there's an error (for example, if the user says they're 250 years old), the bot requests new input. By `/cancel`, the process stops and the bot returns to normal mode. Look at the diagram below:

![A process consisting of three steps](../images/ru/fsm/l04_1.svg)

The **green** arrows represent transitions between steps without errors. The **blue** arrows represent staying in the current state and waiting for a corrected entry (for example, if the user provides an invalid age). The **red** arrows represent exiting the entire process due to `/cancel` or similar cancellation commands.

This process is called a **finite state machine** (or FSM — Finite State Machine) in algorithm theory. You can read more about it [here](https://tproger.ru/translations/finite-state-machines-theory-and-implementation/).

!!! info "Dialog constructor"
    After practicing with FSM in this chapter, you'll likely realize how much code is needed for complex branching dialogs. Fortunately, the [**aiogram-dialog**](https://github.com/Tishka17/aiogram_dialog) library by **Tishka17** simplifies working with state machines.

## Practice {: id="practice" }

aiogram includes built-in support for various storage backends for persisting states between dialog steps (you can also write your own). Besides state, you can store arbitrary data, such as the user's name and age for later use. A list of available FSM storage backends can be found [in the aiogram repository](https://github.com/aiogram/aiogram/tree/dev-3.x/aiogram/fsm/storage). In this chapter, we'll use the simplest backend: [MemoryStorage](https://github.com/aiogram/aiogram/blob/dev-3.x/aiogram/fsm/storage/memory.py), which stores all data in RAM. It's perfect for examples, but **not recommended** for production because MemoryStorage keeps all data in memory without persisting to disk. Also note that finite state machines can be used not only with message handlers (`message_handler`, `edited_message_handler`), but also with callbacks and inline mode.

As an example, we'll create a small cafe food and drink ordering bot.

### Creating steps {: id="define-states" }

Before we implement FSM, let's quickly write a simple helper function that generates a reply keyboard with buttons in a single row. We'll need it later:

```python title="keyboards/simple_row.py"
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Creates a reply keyboard with one row of buttons
    :param items: list of button texts
    :return: reply keyboard object
    """
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)
```

Let's describe the steps for the "food order" process. We'll create the file `handlers/ordering_food.py` where we'll define the available food names and sizes (in real applications, this information can be loaded dynamically from a database):

```python
# These values will be interpolated into the final message text,
# which is why the adjective forms may look unusual at first glance
available_food_names = ["Sushi", "Spaghetti", "Khachapuri"]
available_food_sizes = ["Small", "Medium", "Large"]
```

Now let's describe all possible "states" of this process (food selection). In words: the user calls `/food`, the bot responds with a request to choose a dish and enters the state *waiting for dish selection* for that specific user. As soon as the user makes a selection, the bot, in that state, validates the input. Then it decides whether to ask for new input (without changing state) or move to the next step *waiting for portion size selection*. When the user enters correct data, the bot displays the order summary (what was ordered) and clears the state. Later in this chapter, we'll learn how to force clear the state at any step using the `/cancel` command.

### Handling step 1 {: id="step-1" }

Now let's implement the states. To store states, we need to create a class that inherits from `StatesGroup`. Inside it, we create variables assigned to instances of the `State` class:

```python
class OrderFood(StatesGroup):
    choosing_food_name = State()
    choosing_food_size = State()
```

Let's write a handler for the first step that responds to the `/food` command when the user has no active state:

```python hl_lines="4 10"
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

@router.message(StateFilter(None), Command("food"))
async def cmd_food(message: Message, state: FSMContext):
    await message.answer(
        text="Choose a dish:",
        reply_markup=make_row_keyboard(available_food_names)
    )
    # Set the user's state to "choosing food name"
    await state.set_state(OrderFood.choosing_food_name)
```

To work with FSM, you must inject an argument named `state` with type `FSMContext` into the handler. In the last line, we explicitly tell the bot to enter the `choosing_food_name` state from the `OrderFood` group.

!!! warning "Difference from aiogram 2.x"
    In aiogram 2.x, the absence of a state filter meant "only when no state is explicitly set" (i.e., `state=None`). In aiogram 3.x, the absence of a filter means "at any state". This is similar to how aiogram 3.x handles message content types.

Next, let's write a handler that matches one of the dish options from our list:

```python linenums="1"
@router.message(
    OrderFood.choosing_food_name, 
    F.text.in_(available_food_names)
)
async def food_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_food=message.text.lower())
    await message.answer(
        text="Thank you. Now please choose the portion size:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
    await state.set_state(OrderFood.choosing_food_size)
```

Let's look at some key elements of this handler. The filters (lines 2-3) specify that the handler will execute only when the user is in the `OrderFood.choosing_food_name` state and the message text matches one of the items in `available_food_names`. On line 6, we store data (the message text) in FSM storage. This data is unique for the pair `(chat_id, user_id)` (there's a nuance we'll cover later). Finally, on line 11 we move the user to the `OrderFood.choosing_food_size` state.

What if the user enters something manually, without using the keyboard? In that case, we should inform the user about the error and give them another chance. A common question from beginner bot developers at this point is: "How do I keep the user in the same state?" The answer is simple: to keep a user in the current state, just don't change it — literally do nothing.

Let's write an additional handler with a filter only on the `OrderFood.choosing_food_name` state, but without a text filter. If we place it after the `food_chosen()` function, it will "handle the state choosing_food_name for all texts except those caught by the previous handler" (in other words, "catch all incorrect inputs").

```python
@router.message(OrderFood.choosing_food_name)
async def food_chosen_incorrectly(message: Message):
    await message.answer(
        text="I don't know such a dish.\n\n"
             "Please choose one of the dishes from the list below:",
        reply_markup=make_row_keyboard(available_food_names)
    )
```

### Handling step 2 {: id="step-2" }

The second and final stage is to handle the user's portion size input. Similar to the previous stage, we'll create two handlers (for correct and incorrect answers). In the first one, we'll add displaying a summary of the order:

```python hl_lines="3 9"
@router.message(OrderFood.choosing_food_size, F.text.in_(available_food_sizes))
async def food_size_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text=f"You selected a {message.text.lower()} portion of {user_data['chosen_food']}.\n"
             f"Now try ordering drinks: /drinks",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@router.message(OrderFood.choosing_food_size)
async def food_size_chosen_incorrectly(message: Message):
    await message.answer(
        text="I don't know such a portion size.\n\n"
             "Please choose one of the sizes from the list below:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
```

The call to `get_data()` on line 3 returns the storage object for that specific user in that specific chat. From it, we retrieve the saved dish name and insert it into the message. The `clear()` method on state returns the user to an "empty" state and deletes all stored data. What if you need to clear only the state or only the data? Let's look at the definition of `clear()` in aiogram 3.x:

```python
class FSMContext:
    # Some code omitted

    async def clear(self) -> None:
        await self.set_state(state=None)
        await self.set_data({})
```

Now you know how to clear just one part :)

Steps for drink selection are implemented similarly. Try doing it yourself or check the source code for this chapter.

Here's the complete file with handlers for food ordering:

```python title="handlers/ordering_food.py"
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.simple_row import make_row_keyboard

router = Router()

# These values will be interpolated into the final message text,
# which is why the adjective forms may look unusual at first glance
available_food_names = ["Sushi", "Spaghetti", "Khachapuri"]
available_food_sizes = ["Small", "Medium", "Large"]


class OrderFood(StatesGroup):
    choosing_food_name = State()
    choosing_food_size = State()


@router.message(Command("food"))
async def cmd_food(message: Message, state: FSMContext):
    await message.answer(
        text="Choose a dish:",
        reply_markup=make_row_keyboard(available_food_names)
    )
    # Set the user's state to "choosing food name"
    await state.set_state(OrderFood.choosing_food_name)

# Food selection step #


@router.message(OrderFood.choosing_food_name, F.text.in_(available_food_names))
async def food_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_food=message.text.lower())
    await message.answer(
        text="Thank you. Now please choose the portion size:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
    await state.set_state(OrderFood.choosing_food_size)


# In general, you can also specify states as full strings.
# This can be useful if for some reason your state names
# are generated at runtime (but why would you do that?)
@router.message(StateFilter("OrderFood:choosing_food_name"))
async def food_chosen_incorrectly(message: Message):
    await message.answer(
        text="I don't know such a dish.\n\n"
             "Please choose one of the dishes from the list below:",
        reply_markup=make_row_keyboard(available_food_names)
    )

# Portion size selection step and order summary display #


@router.message(OrderFood.choosing_food_size, F.text.in_(available_food_sizes))
async def food_size_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(
        text=f"You selected a {message.text.lower()} portion of {user_data['chosen_food']}.\n"
             f"Now try ordering drinks: /drinks",
        reply_markup=ReplyKeyboardRemove()
    )
    # Clear state and stored data for the user
    await state.clear()


@router.message(OrderFood.choosing_food_size)
async def food_size_chosen_incorrectly(message: Message):
    await message.answer(
        text="I don't know such a portion size.\n\n"
             "Please choose one of the sizes from the list below:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
```

### Common commands {: id="common-commands" }

Since we're talking about clearing states, let's implement handlers for `/start` and "cancel" actions in the file `handlers/common.py`. In the first case, a welcome/reference message should be displayed. For cancellation, we'll write two handlers: one for when the user is not in any state, and one for when they are.

All functions guarantee the absence of state and data, and they remove the reply keyboard if it's present:

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
        text="Choose what you want to order: "
             "food (/food) or drinks (/drinks).",
        reply_markup=ReplyKeyboardRemove()
    )


# It's easy to see that the next two handlers could be
# easily combined into one, but we'll keep them separate for clarity

# default_state is the same as StateFilter(None)
@router.message(StateFilter(None), Command(commands=["cancel"]))
@router.message(default_state, F.text.lower() == "cancel")
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    # No need to clear state, just clear data
    await state.set_data({})
    await message.answer(
        text="Nothing to cancel",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "cancel")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Action cancelled",
        reply_markup=ReplyKeyboardRemove()
    )

```

### The bot.py file {: id="entrypoint" }

Finally, let's look at the entry point — the `bot.py` file with all imports and connected routers:

```python title="bot.py"
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# The config_reader.py file can be taken from the repository
# Example is in the first chapter
from config_reader import config
from handlers import common, ordering_food


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # If storage is not specified, MemoryStorage will be used by default anyway
    # But explicit is better than implicit =]
    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(config.bot_token.get_secret_value())

    dp.include_router(common.router)
    dp.include_router(ordering_food.router)
    # Import your own router for drinks here

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
```

### Various FSM strategies {: id="strategies" }

aiogram 3.x introduced an interesting feature to the finite state machine mechanism — FSM strategies. They allow you to redefine the logic for creating state and data pairs. There are five strategies in total:

* **USER_IN_CHAT** — the default strategy. Each user has different states and data in each chat. That is, a user will have different states and data in different groups, as well as in direct messages with the bot.
* **CHAT** — the state and data are shared by the entire chat. In direct messages, the difference is unnoticeable, but in a group, all participants will have one state and shared data.
* **GLOBAL_USER** — a user will have the same state and data across all chats.
* **USER_IN_TOPIC** — a user can have different states depending on the topic in a [supergroup with topics](https://telegram.org/blog/topics-in-groups-collectible-usernames#topics-in-groups).
* **CHAT_TOPIC** — each topic has its own state without division among users in that topic.

Honestly, I can't think of a good use case for **GLOBAL_USER**, but **CHAT** might be useful for bots that implement various games in groups. If you know interesting applications, please tell us in our chat!

As an example, consider a situation where the food ordering bot is in a group and has a **CHAT** strategy. To make this happen, we need to make small changes to the `bot.py` file:

```python
# New import
from aiogram.fsm.strategy import FSMStrategy

async def main():
    # Some code here
    dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)
    # More code here
```

After running the bot, let's ask people in the group to interact with it:

![All users are the same to the bot](../images/ru/fsm/fsm_chat_strategy.png)

Looks strange, right?

Now, armed with knowledge of finite state machines, you can confidently write bots with dialog systems.

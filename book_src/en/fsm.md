---
title: Finite State Machines (FSM)
description: Finite State Machines (FSM)
---

# Finite State Machines (FSM) {: id="fsm-start" }

!!! info ""
    aiogram version used: 3.7.0

## Theory {: id="theory" }

In this chapter, we’ll discuss another essential bot capability: a **dialog system**.
Not every bot task can be completed in a single message or command.

Imagine a dating bot registration flow where a user must provide a name, age, and a face photo.
You *could* ask users to send everything in one caption, but that is inconvenient to validate,
and even more inconvenient when you need to request a correction.

Now consider a step-by-step flow: at the start, the bot enters a state where it waits for specific input
from a specific user. At each step, input is validated. If needed, the bot asks again.
And by `/cancel`, the process stops and the bot returns to normal mode.

This kind of process is called a **finite state machine** (FSM).
You can read more theory [here](https://tproger.ru/translations/finite-state-machines-theory-and-implementation/).

!!! info "Dialog constructor"
    After practicing plain FSM, you’ll likely notice how much boilerplate appears in large branching dialogs.
    In such cases, look at [**aiogram-dialog**](https://github.com/Tishka17/aiogram_dialog),
    which simplifies complex conversational flows.

## Practice {: id="practice" }

aiogram FSM supports multiple storage backends for persisting state between dialog steps.
Besides state itself, you can store arbitrary data (for example, chosen food, size, and later drinks).

In this chapter we use
[MemoryStorage](https://github.com/aiogram/aiogram/blob/dev-3.x/aiogram/fsm/storage/memory.py),
the simplest backend.
It is excellent for examples, but **not recommended** for production because data is kept only in RAM.

As a practical example, we build a small “cafe order” flow.

### Defining steps {: id="define-states" }

Before FSM handlers, let’s define a helper that builds a one-row reply keyboard:

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

Now define available food names and sizes (in real projects this can come from a database):

```python
# These values will be interpolated into final text later,
# which is why adjective forms may look unusual at first glance
available_food_names = ["Sushi", "Spaghetti", "Khachapuri"]
available_food_sizes = ["Small", "Medium", "Large"]
```

Then define process states using `StatesGroup` and `State`:

```python
class OrderFood(StatesGroup):
    choosing_food_name = State()
    choosing_food_size = State()
```

### Handling step 1 {: id="step-1" }

First, handle `/food` when no active state is set:

```python hl_lines="4 10"
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

@router.message(StateFilter(None), Command("food"))
async def cmd_food(message: Message, state: FSMContext):
    await message.answer(
        text="Choose a dish:",
        reply_markup=make_row_keyboard(available_food_names)
    )
    # Set user state: choosing dish name
    await state.set_state(OrderFood.choosing_food_name)
```

To work with FSM in a handler, inject `state: FSMContext`.
Calling `set_state()` explicitly moves the user to the next dialog state.

### Handling step 2 {: id="step-2" }

On the second step, process the selected portion size.
If input is valid, compose the final message, then clear state and data.

The important part is that `await state.clear()` does two things:

- resets state to `None`
- clears stored FSM data

## Additional Materials {: id="extras" }

- Source chapter in Russian: `/fsm/`
- Example code: `code/ru/07_fsm/`

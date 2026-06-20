---
title: Guest Mode
description: Guest Mode
---

# Guest Mode  {: id="guest-mode-start" }

!!! info ""
    aiogram version used: 3.28.0.  
    This is a draft chapter, written shortly after the Bot API v10.0 release.

## Introduction {: id="intro" }

Guest mode allows bots to send messages in chats where they are not members. Their operation algorithm is as follows:

* A user invokes the bot with a message like `@bot QUERY_TEXT`.
* The bot receives the message it was invoked with directly and, if the user's message is a reply to some other message, it also receives that other message (i.e., the `message` will also contain `.reply_to_message`).
* The bot can reply exactly once and only within a short time period.

![Comparison of guest mode and inline mode](../images/ru/guest_bots/intro_dark.png#only-dark)
![Comparison of guest mode and inline mode](../images/ru/guest_bots/intro_light.png#only-light)

Visually and architecturally, guest mode and inline mode are related. Architecturally, Guest Mode looks like inline mode with one selection option, and the message is sent on behalf of the bot itself.

A question may arise: when to use one mode or the other. The official documentation provides [several examples](https://core.telegram.org/bots/features#use-cases-guest-mode-vs-inline-mode), I'll try to rephrase them in my own words. Inline mode is convenient when a person wants to prepare some message with the help of a bot, for example, find an image, video, link, without leaving the chat context in Telegram. Example: invoke the `@pic` bot to quickly find an image and send it on their behalf.

Guest mode is suitable when you need to give a task to a bot from anywhere, without adding it to a group or directly to a DM with another bot. Example: the famous "@grok is this true?" from X/Twitter. The difference is in the level of human involvement in the process and how synchronous the process is. Inline mode assumes that a person inputs all the data, considers the options, and sends the desired one to the chat. Guest mode is "fire and forget", i.e., you nudge the bot and continue chatting anywhere, while the bot performs the task. Look at the screenshot above to see the similarities and differences.

It is important to understand: guest mode does not give the invoked bot access to messages other than one or two (the message with which the bot was invoked and the message that invoked the bot). The guest bot also does not automatically join the group; however, unlike an inline bot, a bot in guest mode receives information about the chat in which it was invoked (ID, name, etc.). There is also an issue with deleting messages: the bot cannot delete its message sent from guest mode because `inline_message_id` is returned upon sending, which is not accepted as input to `deleteMessage()` in the API, and the person invoking the guest bot in the group may not be an administrator. The only option is to send a button with the message that, when clicked, edits the message to be "empty" (a dot or space), but the message itself will still remain.


Let's move on to examples, of which there will be two today: one very simple for understanding the process, and another more complex with some AI features. But first, you need to enable guest mode support for the bot: open the web app of `@BotFather` (specifically the web app!), then select your bot from the list, open `Bot Settings`, and enable `Guest Chat Mode`:

![Comparison of guest mode and inline mode](../images/ru/guest_bots/guest_chat_enable.png)


## Simple Example {: id="simple-example" }

In the simple example, we implement the most basic logic: for any invocation of the bot in guest mode, it will respond with some "uncertain" phrase. This is more than enough to understand the essence and easy reproduction.

_In the block below, you can switch between "handler only" and "complete example" mode._


=== "Handler Only"
    ```python
    RESPONSES = [
        "I don't know.",
        "I'm not sure.",
        "Maybe.",
        "Hard to say.",
        "Possibly.",
    ]

    @dp.guest_message(F.text)  # [1]
    async def any_message(
            message: Message,
    ):
        await message.answer_guest_query(     # [2]
            result=InlineQueryResultArticle(  # [3]
                id="1",
                title="Any text, no one will see it anyway",
                input_message_content=InputTextMessageContent(
                    message_text=random.choice(RESPONSES),
                ),
            )
        )
    ```
    

=== "Complete Example"
    ```python title="simple_example.py"
    --8<-- "code/10_guest_mode/simple_example.py"
    ```

The numbers in the "handler only" block denote:

1. For messages in guest mode, a separate `guest_message` handler is used, since this is a separate update from Telegram. Filters are the same as those for `message`.
2. To respond, call the special method `answer_guest_query()`, attempting to call `answer()` or `reply()` will result in an error.
3. As the only argument `result` of the `answer_guest_query()` function, specify one object of type [InlineResultQuery](https://core.telegram.org/bots/api#inlinequeryresult) (in inline mode a list is passed, but here – a single value). The fields `id` and `title` need to be filled in, but their values don't matter, neither the user nor you will see them anywhere.

If you use `uv`, the startup process is as simple as possible:

```bash
uv add "aiogram>=3.28.0"
BOT_TOKEN=1234567890:AaBbCcDdEeFfGrOoShAHhIiJjKkLlMmNnOo uv run simple_example.py
```

The result is shown in the screenshot below:

![Simple example](../images/ru/guest_bots/simple_example_result_dark.png#only-dark)
![Simple example](../images/ru/guest_bots/simple_example_result_light.png#only-light)


## Advanced Example {: id="advanced-example" }

Next up is to create a simple LLM assistant on a minimal budget: no Internet search, no calling various tools, just through the internal knowledge of some model from [OpenRouter](https://openrouter.ai). To reproduce the following code, you will need your own account on OpenRouter and an API key created there. If you don't have the ability to issue such a key, even from another provider, at least look at the example to the end, so that in the future you can quickly get to work with AI.

All source code for this chapter is located on [GitHub](https://github.com/MasterGroosha/aiogram-3-guide/tree/master/code/10_guest_mode), and below we will consider only the important points.

One of the most important things is the prompt. Let's set the model context, tell it to respond only with unformatted text, describe the logic for processing messages and replies to other messages, and let it respond briefly, to try not to exceed the 4096 character limit. And at the end, let's specify the current date so the AI doesn't think the calendar shows 2024 or 2025:

??? "Prompt text (click to expand)"

    --8<-- "code/10_guest_mode/bot/system_prompt.txt"

Next, the function to get a response from the provider:

```python
async def get_llm_response(
        client: AsyncOpenAI,
        prompt: str,
        model: str,
) -> str | None:
    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
        ],
        stream=False,
        extra_body={"reasoning": {"enabled": True}},
    )
    if not completion.choices:
        return None
    return completion.choices[0].message.content
```

Here it is important to note the following: first, all user messages in our case fit into the system prompt, so the `messages` list will consist of one element. Second, streaming must be disabled; in the case of guest bots, it is not supported. Third, "reasoning" can be set to `False`, then the response will be much faster, but OpenRouter occasionally writes an error that for certain requests or models, enabled reasoning is required, so let's just enable it. Yes, this will slow down getting the response, but guest bots work "in the background", so it's fine. Fourth, sometimes the model doesn't return any result at all, this needs to be handled (in the code above – checking `completion.choices` for emptiness or `None`).

Finally, the handler. It is clear and linear, here it is in full:

```python
@router.guest_message(F.text)
async def guest_message(
        message: Message,
        llm_client: AsyncOpenAI,
        llm_model: str,
        system_prompt: str,
) -> None:
    # Check if the invoking message is a reply to some other message.
    if (replied_message := message.reply_to_message) is None:
        # This will go into the system prompt
        replied_message = "(none provided)"
    else:
        replied_message = (
            replied_message.text
            or f"(some mediafile, contents unknown, "
               f"but there is a caption: {replied_message.caption})"
            # We don't know how to "read" media files
            or "(some mediafile, contents unknown)"
        )
    # Preparing the system prompt
    prompt = (
        system_prompt
        .replace("{{replied_message}}", replied_message)
        .replace("{{current_message}}", message.text)  # noqa
        .replace("{{date_today}}", datetime.now().strftime("%d.%m.%Y"))
    )
    response_text = await get_llm_response(
        client=llm_client,
        prompt=prompt,
        model=llm_model,
    )
    parse_mode = None
    # Sometimes there's no response from the model. In that case, use a placeholder.
    if response_text is None:
        response_text = "<i>Unfortunately, it was not possible to get a response from the model.</i>"
        parse_mode = ParseMode.HTML
    # Respond to the original request
    await message.answer_guest_query(
        result=InlineQueryResultArticle(
            id="1",
            title=".",
            input_message_content=InputTextMessageContent(
                message_text=response_text,
                parse_mode=parse_mode,
            ),
        )
    )
```

The system prompt is read and loaded into RAM each time the bot starts, and the client for working with OpenRouter is initialized there:

```python title="bot/__main__.py"

...

async def main() -> None:
    settings = Settings()

    ...
    
    openrouter_client = AsyncOpenAI(
        base_url=settings.llm.base_url,
        api_key=settings.llm.api_key.get_secret_value(),
    )

    with open("bot/system_prompt.txt", "r", encoding="utf-8") as f:
        system_prompt: str = f.read()

    dp = Dispatcher(
        llm_client=openrouter_client,
        llm_model=settings.llm.model_name,
        system_prompt=system_prompt,
    )

...
```


Add the missing libraries, fill in the `settings.toml` file by analogy with `settings.example.toml`, and run the bot:

```bash
uv add structlog pydantic-settings openai
uv run -m bot
```

Now you can test a couple of scenarios. For example, the bot can't read pictures, but can it roughly guess what's in them, having only a description?

![The bot guessed the contents of an image from a description](../images/ru/guest_bots/advanced_cloudflare_dark.png#only-dark)
![The bot guessed the contents of an image from a description](../images/ru/guest_bots/advanced_cloudflare_light.png#only-light)

Well, that worked out pretty well. How about a message chain and a "sense" of time?

![The bot knows the current date and Durov's age](../images/ru/guest_bots/advanced_durov_dark.png#only-dark)
![The bot knows the current date and Durov's age](../images/ru/guest_bots/advanced_durov_light.png#only-light)

That's also correct (this text was prepared on May 10, 2026). As you can see, even without advanced features like web search and tool calling, you can get a fairly useful everyday tool. This completes our introduction to guest mode for bots.

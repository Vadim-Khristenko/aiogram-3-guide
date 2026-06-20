---
title: 客人模式（Guest mode）
description: 客人模式（Guest mode）
---

# 客人模式  {: id="guest-mode-start" }

!!! info ""
    使用的 aiogram 版本: 3.28.0。  
    这是在 Bot API v10.0 更新发布后"趁热打铁"编写的章节草稿

## 介绍 {: id="intro" }

客人模式允许机器人在它们不是参与者的聊天中发送消息。它们的工作算法如下：

* 用户用 `@bot 请求文本` 形式的消息调用机器人。
* 机器人接收它被调用的直接消息，如果用户的消息是对其他消息的回复（reply），那么它也接收那条其他消息（即在 `message` 中还会有 `.reply_to_message`）。
* 机器人只能在短时间内恰好回复一次。

![客人模式和内联模式的比较](../images/ru/guest_bots/intro_dark.png#only-dark)
![客人模式和内联模式的比较](../images/ru/guest_bots/intro_light.png#only-light)

在视觉上和架构上，客人模式和内联模式是亲戚。架构上，Guest Mode 看起来像一个单一选项的内联模式，消息由机器人本身代表发送。

可能会出现这样的问题：何时使用哪种模式。官方文档给出了 [几个示例](https://core.telegram.org/bots/features#use-cases-guest-mode-vs-inline-mode)，我将尝试用自己的话重新讲述它们。内联模式很方便，当一个人想要在使用机器人的帮助下准备某条消息时，例如，找到一张图片、视频、链接，而不离开 Telegram 中的聊天上下文。示例：调用 `@pic` 机器人以快速找到图像并从自己的名字发送它。

客人模式适用于需要从任何地方给机器人一个任务的情况，而不是将其添加到组或直接与另一个机器人到 LS。示例：著名的来自 X/Twitter 的 "@grok is this true?"。区别在于一个人在这个过程中的参与程度，以及这个过程有多同步。内联模式意味着一个人输入所有数据，查看选项并将所需的发送到聊天。客人模式 - 这是"fire and forget"，即戳机器人，继续在任何地方聊天，而机器人执行任务。看看上面的截图，以了解相似之处和差异。

重要的是要理解：客人模式不给被召唤的机器人访问消息的权限，除了一两条（机器人被调用的消息和调用机器人的消息）。客人机器人也不会自动加入组，但与内联机器人不同，客人模式中的机器人获取关于在其中被调用的聊天的信息（ID、名称等）。同时，删除消息也存在问题：机器人无法删除从客人模式发送的消息，因为发送时返回的是 `inline_message_id`，它不被接受作为 API 中 `deleteMessage()` 的输入，而在组中调用客人机器人的人可能不是管理员。唯一的方法是随消息一起发送一个按钮，点击它可以将消息编辑为"空"（点或空格），但消息本身会保留。

让我们继续进行示例，今天将有两个示例：一个非常简单，便于理解该过程，另一个更复杂，具有一些 AI 功能。但首先，我们需要为机器人启用客人模式支持：在 `@BotFather` 中打开网络应用（正是网络应用！），然后从列表中选择您的机器人，打开 `Bot Settings` 并启用 `Guest Chat Mode`：

![比较客人模式和内联模式](../images/ru/guest_bots/guest_chat_enable.png)


## 简单示例 {: id="simple-example" }

在简单的示例中，我们将实现最基本的逻辑：对于客人模式中的任何机器人调用，它将用某种"犹豫不决"的短语进行响应。这对于理解本质和轻松重现已经足够了。

_在下面的块中，您可以在"仅处理程序"和"完整示例"模式之间切换。_


=== "仅处理程序"
    ```python
    RESPONSES = [
        "我不知道。",
        "我不确定。",
        "也许吧。",
        "很难说。",
        "可能。",
    ]

    @dp.guest_message(F.text)  # [1]
    async def any_message(
            message: Message,
    ):
        await message.answer_guest_query(     # [2]
            result=InlineQueryResultArticle(  # [3]
                id="1",
                title="任何文本，无论如何没有人会看到",
                input_message_content=InputTextMessageContent(
                    message_text=random.choice(RESPONSES),
                ),
            )
        )
    ```
    

=== "完整示例"
    ```python title="simple_example.py"
    --8<-- "code/10_guest_mode/simple_example.py"
    ```

块中的数字"仅处理程序"表示：

1. 对于客人模式中的消息，使用单独的处理程序 `guest_message`，因为这是来自 Telegram 的单独更新。过滤器与 `message` 的过滤器完全相同。
2. 要回复，请调用特殊方法 `answer_guest_query()`，尝试调用 `answer()` 或 `reply()` 会导致错误。
3. 作为 `answer_guest_query()` 函数的唯一参数 `result`，指定一个 [InlineResultQuery](https://core.telegram.org/bots/api#inlinequeryresult) 类型的对象（在内联模式中，传递列表，此处 - 单个值）。需要填充 `id` 和 `title` 字段，
4. 但它们的值不起任何作用，您和用户都看不到它们。

如果您使用 `uv`，启动过程是最简单的：

```bash
uv add "aiogram>=3.28.0"
BOT_TOKEN=1234567890:AaBbCcDdEeFfGrOoShAHhIiJjKkLlMmNnOo uv run simple_example.py
```

结果 - 在下面的截图中：

![简单示例](../images/ru/guest_bots/simple_example_result_dark.png#only-dark)
![简单示例](../images/ru/guest_bots/simple_example_result_light.png#only-light)


## 高级示例 {: id="advanced-example" }

接下来是创建一个最小的 LLM 助手：没有互联网搜索，没有调用各种工具，只是由于 [OpenRouter](https://openrouter.ai) 中某个模型的内部知识。要重复以下代码，您需要在 OpenRouter 上拥有自己的帐户并在那里创建 API 密钥。如果您没有机会发出这样的密钥，即使来自另一个提供商，至少看完这个例子，以便将来快速开始使用 AI。

本章的所有源代码位于 [GitHub](https://github.com/MasterGroosha/aiogram-3-guide/tree/master/code/10_guest_mode) 上，下面的文本只会考虑重要时刻。

最重要的事情之一是提示。让我们为模型设置上下文，说只用未格式化的文本进行响应，描述消息处理和对另一条消息的回复的逻辑，以及让它简洁回复，以尽量不超过 4096 个字符的限制。最后，让我们写下当前日期，这样 AI 就不会认为日历上是 2024 或 2025 年：

??? "提示文本（单击以展开）"

    --8<-- "code/10_guest_mode/bot/system_prompt.txt"

接下来是从提供商获取响应的函数：

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

这里重要的是注意以下几点：首先，在我们的情况下，所有用户消息都适合系统提示，因此 `messages` 列表将由一个元素组成。其次，必须禁用流式传输，在客人机器人的情况下不支持。第三，"推理"（reasoning）可以设置为 `False`，那么响应会快得多，但 OpenRouter 定期写入错误，说某些请求或模型需要启用的推理，所以让我们启用它。是的，这会减慢获取响应的速度，但客人机器人在"后台"工作，所以没关系。第四，有时模型根本不返回任何结果，这需要处理（在上面的代码中 - 通过检查 `completion.choices` 是否为空或 `None`）。

最后，处理程序。它是清晰和线性的，这是完整的：

```python
@router.guest_message(F.text)
async def guest_message(
        message: Message,
        llm_client: AsyncOpenAI,
        llm_model: str,
        system_prompt: str,
) -> None:
    # 检查调用消息是否是对某条其他消息的回复。
    if (replied_message := message.reply_to_message) is None:
        # 这将进入系统提示
        replied_message = "(none provided)"
    else:
        replied_message = (
            replied_message.text
            or f"(some mediafile, contents unknown, "
               f"but there is a caption: {replied_message.caption})"
            # 考虑我们不会"读取"媒体文件
            or "(some mediafile, contents unknown)"
        )
    # 准备系统提示
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
    # 有时模型没有回应。在这种情况下，让它是一个占位符。
    if response_text is None:
        response_text = "<i>抱歉，无法从模型获取响应。</i>"
        parse_mode = ParseMode.HTML
    # 回复原始请求
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

系统提示在每次运行机器人时读取并放入 RAM 中，OpenRouter 客户端也在那里初始化：

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


添加缺少的库，根据 `settings.example.toml` 的类似方式填充 `settings.toml` 文件并运行机器人：

```bash
uv add structlog pydantic-settings openai
uv run -m bot
```

现在您可以测试几个场景。例如，机器人不能读取图片，但根据描述，它能猜测出大概是什么吗？

![机器人根据描述猜测了图片内容](../images/ru/guest_bots/advanced_cloudflare_dark.png#only-dark)
![机器人根据描述猜测了图片内容](../images/ru/guest_bots/advanced_cloudflare_light.png#only-light)

相当不错。消息链和"时间感觉"呢？

![机器人知道当前日期和 Durov 的年龄](../images/ru/guest_bots/advanced_durov_dark.png#only-dark)
![机器人知道当前日期和 Durov 的年龄](../images/ru/guest_bots/advanced_durov_light.png#only-light)

也是正确的（本文是在 2026 年 5 月 10 日准备的）。如您所见，即使没有高级功能，例如网络搜索和工具调用，您也可以获得一个相当有用的日常工具。这样，对客人模式机器人的熟悉就快结束了。

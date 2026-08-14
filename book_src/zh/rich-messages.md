---
title: 富消息
description: 富消息
---

# 富消息

!!! info ""
    使用的 aiogram 版本: 3.29.0

多年来在 Telegram 中只有三种格式化消息的方式：**plaintext**，即不进行格式化，
**HTML** 和两种变体的 **Markdown**，其中一种已被标注为过时。当神经网络引发热潮时，消息内文本美化的能力开始显得相当匮乏。ChatGPT 能生成漂亮的表格、公式
和带脚注的列表，但在 Telegram 中无法不借助各种权宜之计就把这些全部展示出来。Bot API 的开发者在 Bot API 10.1（2026 年 6 月）的更新中添加了名为 Rich Messages 的功能，旨在解决这个问题。
在本章我们将讨论这些 Messages 到底有多“Rich”。

## 一般信息 {: id="intro" }

那么什么是“富媒体消息”（听起来有点尴尬，所以接下来我会用英语称它们为 Rich Messages 或 RM）？
文档是这样描述它们的：

"> Rich Messages 旨在用于高度结构化的响应：报告、来自 AI 的回答、 
> 文档、技术文章以及其他类似的复杂内容。
> 此类消息同时支持 Rich Markdown 和 Rich HTML。 
> Rich Markdown 使用 GitHub Flavored Markdown，并且可以在同一消息中直接包含受支持的 
> HTML 标签。Rich HTML 为机器人提供通过专用标签对更多格式化功能的更精确控制。"

> 支持的样式包括：  
> - 标题、段落、分隔线、列表和待办事项列表。  
> - 嵌套的行内格式化，包括粗体、斜体、下划线、删除线、剧透、代码、小写和大写。  
> - 带对齐、表题、边框、“条纹”样式、列合并和行合并的表格。  
> - 用于照片、视频和音频文件的媒体块，带有说明和署名。  
> - 块引用、重点引用、可折叠的 details 块、锚点和文档内链接。  
> - 脚注和可被引用的文本。  
> - 完全支持 LaTeX，包括行内公式和块级公式。  
> - 带坐标的地图、拼贴、幻灯片放映等更多内容。  

 > **Rich Messages 的限制**. 对 Rich Messages 适用以下限制：  
> - Rich Messages 的文本中最多 **32768** 个 UTF-8 字符，包括自定义表情的替代文本和公式的源代码。  
> - 最多 **500** 个块，包括嵌套块、列表项、编号列表项、表格行、引用块和块 `details`.  
> - 最多 **16** 级嵌套的格式和块。  
> - 总计最多 **50** 个媒体附件，包括照片、视频和音频文件。  
> - 表格中最多 **20** 列。

RM 看起来确实很棒。如果还没见过它们的实际效果，可以观看 
[文档](https://core.telegram.org/bots/features#advanced-formatting-options) 或在 
官方演示机器人 [@richtextdemobot](https://telegram.dog/richtextdemobot) 中查看。

## 与普通消息的区别 {: id="rich-vs-regular" }

Rich Messages **并不替代** 久经考验的 `sendMessage`，支持 MarkdownV2 和 HTML。
这是两种不同的工具，用于不同的场景：

* **普通消息** (`sendMessage`) — 这是一种适用于简短文本的轻量格式：输入确认、对话中的一句话，
  两行包含加粗词和链接的内容。同样保留一些“独占”功能，比如部分引用
  和将引用转发到其他聊天。

* **Rich Messages** (`sendRichMessage`) — 当你需要发送“复杂”文本时的好选择：报告、文档、
  来自神经网络的长回复。标题、表格、脚注、公式、可折叠块——所有以前不得不通过 PIL 将回复渲染成图片或搞出 ASCII 艺术来实现的内容。这样的消息在需要时也可以
  进行编辑——我们将在[下面](#editing)看看具体如何操作。

换句话说：如果你需要发送简单且简短的「完成 ✅」——这是 `sendMessage`. 
如果你需要发送带表格和脚注、占据半个屏幕的结构化报告——这是 `sendRichMessage`.

还有一个重要的点，值得在进入实践部分之前提一提：
在 RM 中不存在所谓的 "parse mode"：标记语言取决于你选择的哪个函数参数 — `markdown` 或 `html`。显式优于隐式，是吧。

## 如何发送 Rich Message {: id="how-to-send" }

在 Bot API 中，用于发送的是方法 [sendRichMessage](https://core.telegram.org/bots/api#sendrichmessage)，
而内容本身由对象 [InputRichMessage](https://core.telegram.org/bots/api#inputrichmessage) 描述。

在两种不同的标记语言中准备文本的示例:

```python
from aiogram.types import InputRichMessage

# 使用 Markdown 的示例
md_content = InputRichMessage(markdown="# 标题\n\n你好，**世界**!")

# 使用 HTML 的示例 — 相同内容，不同语法
html_content = InputRichMessage(html="<h1>标题</h1><p>你好，<b>世界</b>!</p>")
```

接下来这个对象可以直接通过 `bot.send_rich_message(...)` 发送，或者通过位于 `Message` 的常用快捷方式：`answer_rich()` 和 `reply_rich()`

让我们构建一个有意义的示例，其中包含不同层级的标题、表格、公式和脚注。 这一次
通过 **Rich HTML** 来描述消息——为此只需将文本放入字段 `html`. 文本将作为
单独的常量来描述：

```python title="bot/handlers/rich_send.py"
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InputRichMessage, Message

router = Router(name="rich_send")

REPORT_HTML = """\
<h1>季度报告</h1>
<p>这是一个小示例，展示了 <b>Rich Messages</b> 如何保持结构：这里有 \
标题各个层级、表格、公式和脚注<sup><a name="ref-1"></a><a href="#note-1">1</a></sup>.</p>
<h2>关键指标</h2>
<table>
<tr><th align="left">指标</th><th align="right">之前</th><th align="right">之后</th></tr>
<tr><td align="left">MRR</td><td align="right">$35k</td><td align="right">$42k</td></tr>
<tr><td align="left">活跃聊天</td><td align="right">1 240</td><td align="right">1 510</td></tr>
<tr><td align="left">掉线的机器人</td><td align="right">12</td><td align="right">7</td></tr>
</table>
<h2>一些数学</h2>
<p>增长按简单公式计算：</p>
<tg-math-block>rate = (new - old) / old</tg-math-block>
<blockquote>这是一个块引用。在其中可以包含 <i>斜体</i>、 \
<code>代码</code> 和甚至 <tg-spoiler>剧透</tg-spoiler>.</blockquote>

<footer><a name="note-1"></a><a href="#ref-1">1.</a>这些数字为示例虚构，不代表任何真实情况。 ↩️</footer>
"""


@router.message(Command("sendrich"))
async def cmd_send_rich(
        message: Message,
) -> None:
    await message.answer_rich(
        rich_message=InputRichMessage(html=REPORT_HTML),
    )
```

这里发生了什么：

* 标题使用常见标签 `<h1>`…`<h6>`，段落使用标签 `<p>`. 
* 脚注是真正的交互式的，基于锚点实现双向跳转。 
在正文中，标记是 `<sup>`，其内部有锚点 `<a name="ref-1">`（返回点）和指向脚注文本的链接 `<a href="#note-1">1</a>`。在页脚（第5项）一切则相反。 
带有 name 属性的标签 `<a>` 定义锚点，而 `<a href="#имя">` 是指向该锚点的消息内链接 
(当 `<a href="#">` 为空时，链接会跳到开头). 
* 表格由标签 `<table>` 构成，包含行 `<tr>` 和单元格 `<td>`/`<th>`（表头单元格）。 
对齐由属性 `align` 指定（`left`/`center`/`right`），垂直对齐则由 `valign` 控制。 
还支持 `colspan`/`rowspan`、边框和“条纹”样式。 
* 块级公式是自定义标签 `<tg-math-block>`，内部为普通 LaTeX。Telegram 会自行渲染公式。 
* 页脚 `<footer>` —— 这里包含脚注文本以及返回标记的反向链接 ↩️：锚点 `<a name="note-1">` 
允许“跳转”到脚注下方，而链接 `<a href="#ref-1">` 返回到顶部。 
* 在 `<blockquote>` 内，可以看到行内标签（`<i>`, `<code>`, `<tg-spoiler>`) 在嵌套块中也能工作。 
* 快捷方式 `answer_rich()` 将 `InputRichMessage` 发送到相同的聊天。 
由于我们已填充字段 `html`，Telegram 将文本视为 Rich HTML.

结果如下： 

![富媒体消息](images/rich-messages/sendrich_dark.png#only-dark){ width="600" }
![富媒体消息](images/rich-messages/sendrich_light.png#only-light){ width="600" }

!!! warning "不要忘记转义"
    像在普通的 HTML 格式化中一样，任何不是标签一部分的符号 `<`, `>` 和 `&` 都需要替换为
    `&lt;`, `&gt;` 和 `&amp;`。否则 Telegram 会尝试把文本的一部分当作标签，从而破坏标记。

!!! tip "Markdown 和 HTML 可以混用"
    Rich Markdown 允许将受支持的 HTML 标签直接插入到 markdown 文本中。这在某些块用标签表达更简单而主要文本希望保留为 markdown 时很方便。如果需要对所有格式化功能进行完全控制——就像我们上面做的那样，直接使用 `html` 版本。

## 编辑 Rich Messages {: id="editing" }

我们学会了发送，现在来说说编辑。Bot API 并没有增加像 `editRichMessage` 这样的单独方法：
取而代之的是 [editMessageText](https://core.telegram.org/bots/api#editmessagetext) 增加了一个参数 `rich_message`。
参数 `text` 和 `rich_message` 互斥：必须只传递其中一个。
在 aiogram 中，相应地可以使用熟悉的快捷方式 `edit_text()`。

我们来做个小例子：在收到命令 `/sendrichedit` 时，机器人发送一个发布检查表（todo 列表——这是 RM 的一个“特色”）并带有一个内联按钮，点击该按钮后将把所有项标记为已完成：

```python title="bot/handlers/rich_edit.py"
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputRichMessage,
    Message,
)

router = Router(name="rich_edit")

CHECKLIST_BEFORE = """\
# 发布检查表

进度: **0 / 3**

- [ ] 运行测试
- [ ] 更新文档
- [ ] 部署机器人
"""

CHECKLIST_AFTER = """\
# 发布检查表

进度: **3 / 3** 🎉

- [x] 运行测试
- [x] 更新文档
- [x] 部署机器人
"""


@router.message(Command("sendrichedit"))
async def cmd_send_rich_edit(
        message: Message,
) -> None:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="完成所有项目",
            callback_data="complete_checklist",
        )
    ]])
    await message.answer_rich(                                    # [1]
        rich_message=InputRichMessage(markdown=CHECKLIST_BEFORE),
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "complete_checklist")
async def on_complete_checklist(
        callback: CallbackQuery,
) -> None:
    await callback.message.edit_text(                             # [2]
        rich_message=InputRichMessage(markdown=CHECKLIST_AFTER),  # [3]
    )
    await callback.answer()
```

逐条说明：

1. 快捷方式 `answer_rich()` 接受 `reply_markup`，与普通的 `answer()` 完全相同：可以为 Rich Message 附加任意内联键盘。
2. 编辑 — 通过与普通消息相同的 `edit_text()`。由于我们没有传递 `reply_markup`，编辑后按钮会消失 — 所有事项已完成，已无可按。
3. 我们不是传递参数 `text`，而是传入包含新内容的 `rich_message` —— 普通的 `InputRichMessage`，与发送时完全相同。

![富消息](images/rich-messages/sendrichedit_dark.png#only-dark){ width="500" }
![富消息](images/rich-messages/sendrichedit_light.png#only-light){ width="500" }

## 通过 `sendRichMessageDraft` {: id="streaming" } 进行流式传输

我们来谈谈文本的流式传输。在之前的某次更新中为普通消息引入了 `sendMessageDraft`，Rich Messages 也存在类似的方法。实际上，关于流式传输已经在[另一篇单独说明](../blog/posts/project_threads_llm.md#_3)中有相当详细的介绍，但有必要再重复一次基本原则。

流式传输的工作方式如下：

* 该方法向用户显示 **草稿** — 消息的临时预览。这个草稿是短暂的：它存在大约
  30 秒并会自行消失，不会保留在聊天记录中。
* 草稿有 `draft_id` — 非零标识符。所有带有相同 `draft_id` 的更新，Telegram 会将其动画化为
  同一个草稿的平滑变化，而不会闪烁。
* 当生成完成后，需要“固定”草稿：以普通的 `sendRichMessage` 发送已完成的消息。

```python title="bot/handlers/rich_stream.py"
import asyncio
from random import randint

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import InputRichMessage, Message

router = Router(name="rich_stream")

# 我们将分块打印的最终文本。
FINAL_MARKDOWN = """\
# 什么是草稿的流式输出

方法 `sendRichMessageDraft` 在消息仍在生成时向用户显示**临时预览**
—— 就像逐步输出回复的神经网络助手一样。

## 工作原理

- 草稿是**短暂的**：它存在大约 30 秒并会自动消失。
- 所有具有相同 `draft_id` 的更新，Telegram 会将其动画化为平滑的编辑。
- 要让消息永久保留在聊天中，最后需要用普通的 `sendRichMessage` 发送它。
"""


def _build_chunks(text: str) -> list[str]:                        # [1]
    words = text.split(" ")
    chunks: list[str] = []
    step = 12
    for i in range(step, len(words), step):
        chunks.append(" ".join(words[:i]))
    chunks.append(text)
    return chunks

@router.message(Command("sendrichstream"))
async def cmd_send_rich_stream(
        message: Message,
        bot: Bot,
) -> None:
    # 生成随机草稿 ID
    draft_id = randint(1, 100_000_000)                            # [2]

    # 模拟在“第一个标记”到来之前的初始延迟：
    # 显示空文本的占位符并等待 2 秒。
    await bot.send_rich_message_draft(                            # [3]
        chat_id=message.chat.id,
        draft_id=draft_id,
        rich_message=InputRichMessage(
            markdown="<tg-thinking>思考中...</tg-thinking>"        # [4]
        ),
    )
    await asyncio.sleep(2.0)

    for chunk in _build_chunks(FINAL_MARKDOWN):
        await bot.send_rich_message_draft(
            chat_id=message.chat.id,
            draft_id=draft_id,
            rich_message=InputRichMessage(markdown=chunk),
        )
        await asyncio.sleep(0.7)                                  # [5]
    await message.answer_rich(                                    # [6]
        rich_message=InputRichMessage(markdown=FINAL_MARKDOWN),
    )
```

逐项说明：

1. 出于教学目的，我们将最终文本切成递增的前缀。在本机器人中，它们的位置会是来自 LLM 的令牌，
您会将这些令牌累积到缓冲区并定期以草稿形式发送。
2. `draft_id` 必须为非零。我们使用一个随机数作为这样的标识符。
3. 实际上这是发送下一段文本。请注意，该方法返回 `True`/`False`, \
而不是 `Message` 对象——这并非真正的消息，而是预览。
4. 占位符，可在完全没有文本时显示。顺便说一句，动画很漂亮。
5. 在更新之间稍作暂停，以免触及防刷限额。请根据你的负载调整间隔。
6. 收尾：用普通的 `answer_rich()` 发送完整文本。该消息将会保留在聊天中.

!!! note "不要尝试逐字符地流式传输"
    每次调用 `send_rich_message_draft` — 是一次网络请求。积累一个合理的缓冲区（几个词或一行）
    并每隔几百毫秒发送一次预览，否则 Telegram 很快就会对你施加限流。

在视频中动态演示如下：

![类型:视频](images/rich-messages/streaming_dark.mp4)

## 媒体文件 {: id="media" }

文本并不限于此 — 可以在 RM 中嵌入媒体。这里出现了一个不太令人愉快的特性
Rich Messages: 媒体文件不能通过 `file_id` 传输，只能通过 HTTP(S) 链接。

在 Rich Markdown 中，对于媒体文件支持标准的 Markdown 语法: `![alt-текст](URL "title")`. 然而
带有 alt 文本的部分（在普通网页上，当媒体文件未加载或处于“仅文本”模式时会使用）
在 Telegram 中不会显示，且可见的说明需要在 URL 之后用引号立即指定。
不过，看看下面的示例你就会明白：

```python title="bot/handlers/rich_media.py"
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InputRichMessage, Message

router = Router(name="rich_media")

GALLERY_MARKDOWN = """\
# HTTP 猫咪画廊

在一条富媒体消息中包含多张图片，每张都有说明和标题。

**204 No Content** — 服务器已成功处理请求，但响应体中没有要返回的内容。客户端保持在当前页面，并在需要时根据响应头刷新数据。

![](https://http.cat/images/204.jpg "HTTP 204 No Content")

**301 Moved Permanently** — 请求的资源已永久移动到 `Location` 头中给出的新地址。今后的所有请求和书签都应指向该地址，搜索引擎会随着时间更新链接。

![](https://http.cat/images/301.jpg "HTTP 301 Moved Permanently")

**418 I'm a teapot** — 这是来自愚人节 RFC 2324 的一个玩笑状态码：茶壶服务器坚决拒绝为咖啡冲泡。虽然在真实 API 中不使用，但作为一个受欢迎的彩蛋存在。

![](https://http.cat/images/418.jpg "HTTP 418 I am a Teapot")

在画廊下面可以继续写文本：标题、列表和其他内容照常工作。
"""


@router.message(Command("sendrichmedia"))
async def cmd_send_rich_media(
        message: Message,
) -> None:
    await message.answer_rich(
        rich_message=InputRichMessage(markdown=GALLERY_MARKDOWN),
    )
```

截图中成品消息的顶部:

![富消息](images/rich-messages/sendrichmedia_dark.png#only-dark){ width="500" } 
![富消息](images/rich-messages/sendrichmedia_light.png#only-light){ width="500" } 

!!! note "拼贴、幻灯片和其他媒体"
    几张图片连在一起——这是基本情况。要在 Rich HTML 中精细控制布局，有单独的
    标签： `<photo>`, `<video>` 和 `<audio>` 用于单个媒体，还有自定义的 `<tg-collage>`（拼贴）和
    `<tg-slideshow>`（幻灯片），媒体块被嵌入其中。可以在
    [@richtextdemobot](https://telegram.dog/richtextdemobot) 现场体验渲染。


## 如何捕获并解析 富消息 {: id="parsing" }

除了发送富消息之外，还需要学会接收并“理解”它们。况且，率先掌握这种新消息类型的，正是垃圾邮件发送者。类 [Message](https://core.telegram.org/bots/api#message)
新增了一个名为 `rich_message`、类型为 [RichMessage](https://core.telegram.org/bots/api#richmessage) 的新字段。它会在机器人收到 RM 时被填充。

`RichMessage` 的结构很简单：它是一个区块的列表（`blocks`）。每个区块都有一个通用字段 `type`（`heading`, `paragraph`,
`table`, `list`, `photo`, `slideshow`, `collage`, `footer` 等等），文本区块在字段 `text` 中包含由
`RichText` 组成的树。该树可以是字符串、节点列表或带样式的节点（粗体、斜体……），其内部又包含
`RichText`。要从中提取“纯”文本，写一个小的递归函数会很方便：

```python title="bot/handlers/rich_parse.py"
from collections import Counter

from aiogram import F, Router
from aiogram.types import Message

router = Router(name="rich_parse")


def flatten_text(node) -> str:
    if node is None:
        return ""
    if isinstance(node, str):                                     # [1]
        return node
    if isinstance(node, list):                                    # [2]
        return "".join(flatten_text(item) for item in node)
    # 自定义表情没有嵌套的 text，但有替代文本
    if getattr(node, "type", None) == "custom_emoji":             # [3]
        return node.alternative_text
    return flatten_text(getattr(node, "text", None))              # [4]


@router.message(F.rich_message)                                   # [5]
async def on_rich_message(
        message: Message,
) -> None:
    blocks = message.rich_message.blocks

    stats = "\n".join(f"• {block.type}" for block in blocks)      # [6]

    headings = [                                                  # [7]
        flatten_text(block.text)
        for block in blocks
        if block.type == "heading"
    ]

    table = next((b for b in blocks if b.type == "table"), None)  # [8]

    lines = [
        f"Rich Message 由 {len(blocks)} 个块组成。",
        f"组成：{stats}",
    ]
    if headings:
        toc = "\n".join(f"• {title}" for title in headings)
        lines.append(f"\n标题：\n{toc}")
    if table is not None:
        first_row = " | ".join(flatten_text(cell.text) for cell in table.cells[0])
        lines.append(f"\n表格的第一行：{first_row}")

    await message.answer("\n".join(lines))
```

我们来分解关键点：

1. 递归的基本情况：如果节点 — 普通字符串，就原样返回它。
2. 如果节点 — 列表，将每个元素遍历的结果拼接起来。
3. 自定义表情没有嵌套的 `text`，但有 `alternative_text` — 使用它。
4. 在其他所有情况下这是一个带样式的节点：进入它的字段 `text` 再深入一层。
5. 魔法过滤器 `F.rich_message` 只有在传入消息的字段 `rich_message` 被填充时才会触发。
   这样我们就能捕获富消息，并且不干扰命令。
6. 按出现顺序收集块。
7. 将所有标题收集到目录中。顺便可以看到 `flatten_text` 如何从标题中提取文本，
   即使它被斜体或加粗包裹。
8. 如果内部有表格，则取出它的第一行。单元格位于 `table.cells` 中，作为列表的列表（`строки → ячейки`），
   而单元格的文本又是一个 RichText 树。

如果把机器人转发它自己的带 HTTP 猫的示例，你应该会看到以下消息：

```
Rich Message 由 9 个块。
组成：
• heading
• paragraph
• paragraph
• photo
• paragraph
• photo
• paragraph
• photo
• paragraph

标题：
• HTTP 猫咪画廊
```


## 结论 {: id="conclusion" }

Rich Messages — 这是 Telegram 对神经网络时代和 Markdown 广泛使用的早该有的回应。
在本章中，我们学会了发送此类消息（通过 `markdown`/`html`）、编辑它们、按块解析传入消息并通过临时草稿流式传输回复。镜头之外还有许多块——地图、可折叠的 `details`,
音频和视频、块状公式——但原理到处都是相同的，所以掌握了基础后，其余内容你可以通过 [文档](https://core.telegram.org/bots/api#inputrichmessage) 和 [演示机器人](https://telegram.dog/richtextdemobot) 学会。
---
title: Rich Messages
description: Rich Messages
---

# Rich Messages

!!! info ""
    Using aiogram version: 3.29.0

For many years there were only three ways to format messages in Telegram: **plaintext** (i.e. without formatting), **HTML**, and **Markdown** in two variants, one of which is considered deprecated. When the neural network boom swept the planet, the options for decorating text in the messenger started to look quite meager. ChatGPT generates beautiful tables, formulas, and lists with footnotes, and you couldn't display all of that in Telegram without hacks. The Bot API developers added a feature called Rich Messages in the Bot API 10.1 update (June 2026) to solve this problem. In this chapter we'll talk about these Messages and how Rich they are.

## General information {: id="intro" }

What are "rich messages" (sounds cringe, so I will call them by the English name Rich Messages or RM)? The documentation describes them as:


> Rich Messages are intended for highly structured responses: reports, AI outputs, documentation, technical articles and other similar complex content.
> Such messages support both Rich Markdown and Rich HTML.
> Rich Markdown uses GitHub Flavored Markdown and may include supported HTML tags directly in the same message. Rich HTML gives bots more precise control over even more formatting capabilities using special tags.


> Supported styles include:  
> - Headings, paragraphs, dividers, lists and todo-lists.  
> - Nested inline formatting, including bold, italic, underline, strikethrough, spoiler, code, subscript and superscript.  
> - Tables with alignment, captions, borders, "striped" style, column spanning and row spanning.  
> - Media blocks for photos, videos and audio files, with captions and attribution.  
> - Block quotes, highlighted quotes, collapsible details blocks, anchors and intra-document links.  
> - Footnotes and anchorable text.  
> - Full LaTeX support, including both inline and display equations.  
> - Maps with coordinates, collages, slideshows and more.  


> **Rich Messages limits**. The following limits apply to Rich Messages:  
> - Up to **32768** UTF-8 characters in the rich message text, including alternative text of custom emoji and the original formula source.  
> - Up to **500** blocks, including nested blocks, list items, numbered list items, table rows, quote blocks and blocks `details`.  
> - Up to **16** levels of nested formatting and blocks.  
> - Up to **50** media attachments in total, including photos, videos and audio files.  
> - Up to **20** columns in a table.  

RM do look really great. If you haven't seen them in action yet, you can check out a nice demo in the [documentation](https://core.telegram.org/bots/features#advanced-formatting-options) or in the official demo bot [@richtextdemobot](https://telegram.dog/richtextdemobot).

## Difference from regular messages {: id="rich-vs-regular" }

Rich Messages **do not replace** the good old `sendMessage` with MarkdownV2 and HTML. These are two different tools for different tasks:

* **Regular messages** (`sendMessage`) — a lightweight format for short texts: input confirmations, replies in a conversation, a couple of lines with a bold word and a link. "Exclusive" features like partial quoting and forwarding a quoted message to another chat remain here.

* **Rich Messages** (`sendRichMessage`) — a good option when you need to send "complex" text: a report, documentation, a long response from a neural network. Headings, tables, footnotes, formulas, collapsible blocks — all the things that used to force you to render the reply as an image via PIL or to create ASCII art. Such messages can also be edited when necessary — [below](#editing) we'll see exactly how.

In other words: if you need to send a simple and short "Done ✅" — use `sendMessage`. If you need to send a structured report with tables and footnotes that fills half the screen — use `sendRichMessage`.

One more important point to mention before moving on to the practical part: RMs do not have a concept of a "parse mode": the markup language depends on which function argument you choose — `markdown` or `html`. Explicit is better than implicit, right.

## How to send a Rich Message {: id="how-to-send" }

In the Bot API the method [sendRichMessage](https://core.telegram.org/bots/api#sendrichmessage) is responsible for sending, and the content itself is described by the [InputRichMessage](https://core.telegram.org/bots/api#inputrichmessage) object.

Example of preparing text in two different markup languages:

```python
from aiogram.types import InputRichMessage

# Markdown variant
md_content = InputRichMessage(markdown="# Heading\n\nHello, **world**!")

# HTML variant — the same thing but with different syntax
html_content = InputRichMessage(html="<h1>Heading</h1><p>Hello, <b>world</b>!</p>")
```

You can then send this object either directly via `bot.send_rich_message(...)`, or via the usual shortcuts in `Message`: `answer_rich()` and `reply_rich()`

Let's assemble a meaningful example that involves headings of different levels, a table, a formula, and a footnote. This time
we'll describe the message using **Rich HTML** — to do that it's enough to put the text into the field `html`. We'll describe the text
as a separate constant:

```python title="bot/handlers/rich_send.py"
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InputRichMessage, Message

router = Router(name="rich_send")

REPORT_HTML = """\
<h1>Quarterly Report</h1>
<p>A small example of how <b>Rich Messages</b> preserve structure: here there are \
headings of different levels, a table, a formula, and a footnote<sup><a name="ref-1"></a><a href="#note-1">1</a></sup>.</p>
<h2>Key metrics</h2>
<table>
<tr><th align="left">Metric</th><th align="right">Before</th><th align="right">After</th></tr>
<tr><td align="left">MRR</td><td align="right">$35k</td><td align="right">$42k</td></tr>
<tr><td align="left">Active chats</td><td align="right">1 240</td><td align="right">1 510</td></tr>
<tr><td align="left">Disconnected bots</td><td align="right">12</td><td align="right">7</td></tr>
</table>
<h2>A bit of math</h2>
<p>We calculate growth using a simple formula:</p>
<tg-math-block>rate = (new - old) / old</tg-math-block>
<blockquote>This is a block quote. Inside it you can have <i>italics</i>, \
<code>code</code> and even a <tg-spoiler>spoiler</tg-spoiler>.</blockquote>

<footer><a name="note-1"></a><a href="#ref-1">1.</a>Numbers are fictional for example purposes and do not reflect real data. ↩️</footer>
"""


@router.message(Command("sendrich"))
async def cmd_send_rich(
        message: Message,
) -> None:
    await message.answer_rich(
        rich_message=InputRichMessage(html=REPORT_HTML),
    )
```

What's happening here:

* Headings are set with the usual tags `<h1>`…`<h6>`, paragraphs — with the `<p>` tag.
* The footnote is a real interactive one, working both ways via anchors.
  In the text the marker is `<sup>`, inside which there is an anchor `<a name="ref-1">` (return point) and a link
  `<a href="#note-1">1</a>` to the footnote text. In the footer (item 5) everything is mirrored.
  The tag `<a>` with the name attribute defines an anchor, and `<a href="#имя">` is the link to it inside the message
  (with an empty `<a href="#">` the link goes to the top).
* A table is the `<table>` tag with rows `<tr>` and cells `<td>`/`<th>` (header cells).
  Alignment is set by the `align` attribute (`left`/`center`/`right`), and for vertical alignment there is `valign`.
  `colspan`/`rowspan` are also supported, as well as borders and a "striped" style.
* A block formula is a custom tag `<tg-math-block>`, with regular LaTeX inside. Telegram will render the formula itself.
* The footer `<footer>` contains the footnote text and a back link ↩️ to the marker: the anchor `<a name="note-1">`
  lets you "jump" down to the footnote, and the link `<a href="#ref-1">` returns you back up.
* Inside `<blockquote>` you can see that inline tags (`<i>`, `<code>`, `<tg-spoiler>`) work even in nested blocks.
* The shortcut `answer_rich()` sends `InputRichMessage` to the same chat.
Since we've filled the `html` field, Telegram treats the text as Rich HTML.

The result looks like this: 

![Rich Message](images/rich-messages/en/sendrich_dark.png#only-dark){ width="460" }
![Rich Message](images/rich-messages/en/sendrich_light.png#only-light){ width="460" }

!!! warning "Don't forget to escape"
    As with regular HTML formatting, characters `<`, `>` and `&` that are not part of a tag must be replaced with
    `&lt;`, `&gt;` and `&amp;`. Otherwise Telegram may try to interpret a piece of text as a tag and break the markup.

!!! tip "You can mix Markdown and HTML"
    Rich Markdown allows inserting supported HTML tags directly into markdown text. This is convenient when a certain
    block is easier to express with a tag, while you want to keep the main text in markdown. And if you need full control over all
    formatting capabilities — use the full `html` variant, like we did above.

## Editing Rich Messages {: id="editing" }

We learned how to send them, now about editing. There isn't a separate method like `editRichMessage` in the Bot API:
instead [editMessageText](https://core.telegram.org/bots/api#editmessagetext) gained an
argument `rich_message`. The arguments `text` and `rich_message` are mutually exclusive: you must provide exactly one of them.
In aiogram, correspondingly, the usual shortcut `edit_text()` works.

Let's build a small example: on the `/sendrichedit` command the bot sends a release checklist (a todo list — one of RM's
"features") with an inline button, and when the button is pressed it marks all items as completed:

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
# Release checklist

Progress: **0 of 3**

- [ ] Run tests
- [ ] Update documentation
- [ ] Deploy the bot
"""

CHECKLIST_AFTER = """\
# Release checklist

Progress: **3 of 3** 🎉

- [x] Run tests
- [x] Update documentation
- [x] Deploy the bot
"""


@router.message(Command("sendrichedit"))
async def cmd_send_rich_edit(
        message: Message,
) -> None:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Complete all items",
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

Step by step:

1. The shortcut `answer_rich()` accepts `reply_markup` just like a normal `answer()`: you can attach any inline keyboard to a Rich Message.
2. Editing is done via the familiar `edit_text()` used for ordinary messages. And since we didn't pass `reply_markup`,
   after editing the button will disappear — all items are completed, there's nothing left to press.
3. Instead of the `text` argument we pass `rich_message` with the new content — a regular `InputRichMessage`,
   exactly the same as when sending.

![Rich Message](images/rich-messages/sendrichedit_dark.png#only-dark){ width="500" }
![Rich Message](images/rich-messages/sendrichedit_light.png#only-light){ width="500" }

## Streaming via `sendRichMessageDraft` {: id="streaming" }

Let's talk about streaming text. In one of the previous updates `sendMessageDraft` was introduced for ordinary messages,
and a similar method exists for Rich Messages. In fact, streaming was already covered in detail
[in a separate note](../blog/posts/project_threads_llm.md#_3), but it's worth repeating the general principles.

Streaming works like this:

* The method shows the user a **draft** — a temporary preview of the message. This draft is ephemeral: it lives for about
  30 seconds and then disappears; it does not remain in the chat history.
* The draft has an `draft_id` — a non-zero identifier. All updates with the same `draft_id` are animated by Telegram
  as a smooth change of the same draft, without flickering.
* When generation is finished, the draft must be "committed": send the final message with the regular `sendRichMessage`.

```python title="bot/handlers/rich_stream.py"
import asyncio
from random import randint

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import InputRichMessage, Message

router = Router(name="rich_stream")

# Final text that we will print in chunks.
FINAL_MARKDOWN = """\
# What is draft streaming

The method `sendRichMessageDraft` shows the user a **temporary preview**
of the message while it's still being generated — exactly how neural
assistants behave when they type an answer gradually.

## How it works

- The draft is **ephemeral**: it lives for about 30 seconds and disappears by itself.
- Telegram animates all updates with the same `draft_id` as a smooth edit.
- To make the message remain in the chat permanently, you need to send it
  at the end using a regular `sendRichMessage`.
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
    # Generate a random draft id
    draft_id = randint(1, 100_000_000)                            # [2]

    # Simulate initial delay before the 'first token':
    # show a placeholder for empty text and wait a 2-second pause.
    await bot.send_rich_message_draft(                            # [3]
        chat_id=message.chat.id,
        draft_id=draft_id,
        rich_message=InputRichMessage(
            markdown="<tg-thinking>Thinking...</tg-thinking>"        # [4]
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

Step by step:

1. For demonstration we cut the final text into growing prefixes. In a real bot those would be LLM tokens that you accumulate in a buffer and periodically send as a draft.
2. `draft_id` must be non-zero. Use a random number as such an identifier.
3. The actual sending of the next chunk. Note that the method returns `True`/`False`, \
and not an `Message` object — after all, this is not a real message but a preview.
4. A placeholder you can show while there is no text at all. Nicely animated, by the way.
5. A small pause between updates so you don't hit the flood limits. Adjust the interval to your load.
6. Finale: send the full text with the regular `answer_rich()`. That message will remain in the chat.

!!! note "Don't try to stream character-by-character"
    Every call to `send_rich_message_draft` is a network request. Accumulate a reasonable buffer (a few words or a line)
    and send previews every few hundred milliseconds, otherwise Telegram will quickly throttle you with limits.

How this looks "in action" on video:

![type:video](images/rich-messages/streaming_dark.mp4)

## Media files {: id="media" }

It's not limited to text — you can embed media inside an RM. Here an unpleasant peculiarity of Rich Messages appears: media files cannot be sent via `file_id`, only via HTTP(S) links.

Rich Markdown supports the standard Markdown syntax for media files: `![alt-текст](URL "title")`. However, the alt-text part (on the regular web it's used when a media file fails to load or in "text-only" mode) is not displayed anywhere in Telegram, and the visible caption must be specified immediately after the URL in quotes. Anyway, look at the example below and you'll understand:

```python title="bot/handlers/rich_media.py"
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InputRichMessage, Message

router = Router(name="rich_media")

GALLERY_MARKDOWN = """\
# HTTP Cats Gallery

Several images inside a single rich message, each with a description and a caption.

**204 No Content** — the server successfully processed the request, but there is no content to send in the response body. The client stays on the current page and, if necessary, updates data based on the response headers.

![](https://http.cat/images/204.jpg "HTTP 204 No Content")

**301 Moved Permanently** — the requested resource has permanently moved to the address from the `Location` header. All future requests and bookmarks should be directed there, and search engines will update links over time.

![](https://http.cat/images/301.jpg "HTTP 301 Moved Permanently")

**418 I'm a teapot** — a joke status code from the April Fools' RFC 2324: a teapot server refuses to brew coffee. Not used in real APIs, but lives on as a beloved Easter egg.

![](https://http.cat/images/418.jpg "HTTP 418 I am a Teapot")

You can continue the text below the gallery: headings, lists, and everything else work as usual.
"""


@router.message(Command("sendrichmedia"))
async def cmd_send_rich_media(
        message: Message,
) -> None:
    await message.answer_rich(
        rich_message=InputRichMessage(markdown=GALLERY_MARKDOWN),
    )
```

The top part of the finished message in the screenshot:

![Rich Message](images/rich-messages/sendrichmedia_dark.png#only-dark){ width="500" } 
![Rich Message](images/rich-messages/sendrichmedia_light.png#only-light){ width="500" } 

!!! note "Collage, slideshow and other media"
    Several images in a row are the basic case. For fine-grained layout control in Rich HTML there are separate tags: `<photo>`, `<video>` and `<audio>` for single media, as well as custom `<tg-collage>` (collage) and
    `<tg-slideshow>` (slideshow), into which media blocks are placed. You can try the rendering live at
    [@richtextdemobot](https://telegram.dog/richtextdemobot).


## How to capture and parse a Rich Message {: id="parsing" }

Besides sending Rich Messages, you need to learn how to receive and "understand" them. Especially since one of the first groups to adopt the new message type were spammers. The [Message](https://core.telegram.org/bots/api#message) class gained a new field `rich_message` of type [RichMessage](https://core.telegram.org/bots/api#richmessage). It is populated when the bot receives an RM.

The structure of `RichMessage` is simple: it's a list of blocks (`blocks`). Each block has a common field `type` (`heading`, `paragraph`,
`table`, `list`, `photo`, `slideshow`, `collage`, `footer` etc.), and text blocks carry in the field `text` a tree of `RichText` objects. This tree can be a string, a list of nodes, or a styled node (bold, italic...), inside which there is again
`RichText`. To extract the "plain" text from it, it's convenient to write a small recursive function:

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
    # Custom emojis don't have nested text, but they have alternative text
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
        f"Rich Message contains {len(blocks)} blocks.",
        f"Contents: {stats}",
    ]
    if headings:
        toc = "\n".join(f"• {title}" for title in headings)
        lines.append(f"\nHeadings:\n{toc}")
    if table is not None:
        first_row = " | ".join(flatten_text(cell.text) for cell in table.cells[0])
        lines.append(f"\nFirst row of the table: {first_row}")

    await message.answer("\n".join(lines))
```

Let's go over the key points:

1. Base case of recursion: if a node is a plain string, return it as is.
2. If the node is a list, concatenate the results of processing each element.
3. A custom emoji has no nested `text`, but it does have `alternative_text` — take that.
4. In all other cases it's a styled node: descend into its field `text` one level deeper.
5. The magic filter `F.rich_message` triggers only if the incoming message has the field `rich_message` filled.
   This way we catch specifically rich messages and don't interfere with commands.
6. Collect blocks in the order they appear.
7. Gather all headings into a table of contents. You can also see how `flatten_text` extracts text from a heading,
   even if it's wrapped in italic or bold.
8. If there's a table inside, extract its first row. Cells are stored in `table.cells` as a list of lists (`строки → ячейки`),
   and a cell's text is again a RichText tree.

If you forward the bot its own example with HTTP-kitties, you should see the following message:

```
Rich Message of 9 blocks.
Composition:
• heading
• paragraph
• paragraph
• photo
• paragraph
• photo
• paragraph
• photo
• paragraph

Headings:
• HTTP Kittens Gallery
```


## Conclusion {: id="conclusion" }

Rich Messages are a long-overdue response from Telegram to the era of neural networks and the widespread use of Markdown.
In this chapter we learned how to send such messages (via `markdown`/`html`), edit them, parse incoming messages by blocks, and stream responses through ephemeral drafts. Many blocks remain offstage — maps, collapsible `details`,
audio and video, block formulas — but the principle is the same everywhere, so armed with the basics you'll master the rest
via the [documentation](https://core.telegram.org/bots/api#inputrichmessage) and the [demo bot](https://telegram.dog/richtextdemobot).

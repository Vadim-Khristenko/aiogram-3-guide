import asyncio
import logging
import re
from datetime import datetime

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message, FSInputFile, URLInputFile, BufferedInputFile, LinkPreviewOptions
from aiogram.utils.formatting import as_list, as_marked_section, Bold, as_key_value, HashTag
from aiogram.utils.markdown import hide_link
from aiogram.utils.media_group import MediaGroupBuilder

from config_reader import config

bot = Bot(
    token=config.bot_token.get_secret_value(),
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)


@dp.message(Command("test"))
async def any_message(message: Message):
    await message.answer("你好，<b>世界</b>！", parse_mode=ParseMode.HTML)
    await message.answer("你好，*世界*\!", parse_mode=ParseMode.MARKDOWN_V2)
    await message.answer("带有 <u>HTML 标记</u> 的消息")
    await message.answer("没有 <s>任何标记</s> 的消息", parse_mode=None)


@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    await message.answer(
        f"你好，{html.bold(html.quote(message.from_user.full_name))}",
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("advanced_example"))
async def cmd_advanced_example(message: Message):
    content = as_list(
        as_marked_section(
            Bold("成功："),
            "测试 1",
            "测试 3",
            "测试 4",
            marker="✅ ",
        ),
        as_marked_section(
            Bold("失败："),
            "测试 2",
            marker="❌ ",
        ),
        as_marked_section(
            Bold("总结："),
            as_key_value("总共", 4),
            as_key_value("成功", 3),
            as_key_value("失败", 1),
            marker="  ",
        ),
        HashTag("#test"),
        sep="\n\n",
    )
    await message.answer(**content.as_kwargs())


@dp.message(Command("settimer"))
async def cmd_settimer(
        message: Message,
        command: CommandObject
):
    # 如果没有传递任何参数，那么
    # command.args 将是 None
    if command.args is None:
        await message.answer(
            "错误：没有传递参数"
        )
        return
    # 尝试按第一个空格将参数分成两部分
    try:
        delay_time, text_to_send = command.args.split(" ", maxsplit=1)
    # 如果得不到两部分，将抛出 ValueError
    except ValueError:
        await message.answer(
            "错误：命令格式不正确。例子：\n"
            "/settimer <time> <message>"
        )
        return
    await message.answer(
        "计时器已添加！\n"
        f"时间：{delay_time}\n"
        f"文本：{text_to_send}"
    )


@dp.message(Command("gif"))
async def send_gif(message: Message):
    await message.answer_animation(
        animation="<file_id гифки>",
        caption="我今天：",
        show_caption_above_media=True
    )


@dp.message(Command("custom1", prefix="%"))
async def cmd_custom1(message: Message):
    await message.answer("看到命令了！")


# 可以指定多个前缀...............vv.....
@dp.message(Command("custom2", prefix="/!"))
async def cmd_custom2(message: Message):
    await message.answer("也看到这个了！")


@dp.message(Command("help"))
@dp.message(CommandStart(
    deep_link=True, magic=F.args == "help"
))
async def cmd_start_help(message: Message):
    await message.answer("这是帮助消息")


@dp.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r'book_(\d+)'))
))
async def cmd_start_book(
        message: Message,
        command: CommandObject
):
    book_number = command.args.split("_")[1]
    await message.answer(f"发送书籍第 {book_number} 卷")


@dp.message(Command("links"))
async def cmd_links(message: Message):
    # 两个将进入最终消息的链接
    links_text = (
        "https://nplus1.ru/news/2024/05/23/voyager-1-science-data"
        "\n"
        "https://t.me/telegram"
    )
    # 链接已禁用
    options_1 = LinkPreviewOptions(is_disabled=True)
    await message.answer(
        f"没有链接预览\n{links_text}",
        link_preview_options=options_1
    )

    # -------------------- #

    # 小预览
    # 要使用 prefer_small_media，必须同时指定 url
    options_2 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_small_media=True
    )
    await message.answer(
        f"小预览\n{links_text}",
        link_preview_options=options_2
    )

    # -------------------- #

    # 大预览
    # 要使用 prefer_large_media，必须同时指定 url
    options_3 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_large_media=True
    )
    await message.answer(
        f"大预览\n{links_text}",
        link_preview_options=options_3
    )

    # -------------------- #

    # 可以组合：小预览和文字上方显示
    options_4 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_small_media=True,
        show_above_text=True
    )
    await message.answer(
        f"文字上方的小预览\n{links_text}",
        link_preview_options=options_4
    )

    # -------------------- #

    # 可以选择哪个链接用于预览
    options_5 = LinkPreviewOptions(
        url="https://t.me/telegram"
    )
    await message.answer(
        f"非第一个链接的预览\n{links_text}",
        link_preview_options=options_5
    )



@dp.message(Command("hidden_link"))
async def cmd_hidden_link(message: Message):
    await message.answer(
        f"{hide_link('https://telegra.ph/file/562a512448876923e28c3.png')}"
        f"Telegram 文档：*存在*\n"
        f"用户：*不读文档*\n"
        f"梨："
    )


@dp.message(Command('images'))
async def upload_photo(message: Message):
    # 我们将在此放置已发送文件的 file_id，以便以后使用
    file_ids = []

    # 为了演示 BufferedInputFile，我们将使用"经典"
    # 通过 `open()` 打开文件。但一般来说，这种方法
    # 最适合发送内存中的字节
    # 在进行一些操作后，例如通过 Pillow 编辑
    with open("buffer_emulation.jpg", "rb") as image_from_buffer:
        result = await message.answer_photo(
            BufferedInputFile(
                image_from_buffer.read(),
                filename="image from buffer.jpg"
            ),
            caption="来自缓冲区的图像"
        )
        file_ids.append(result.photo[-1].file_id)

    # 从文件系统发送文件
    image_from_pc = FSInputFile("image_from_pc.jpg")
    result = await message.answer_photo(
        image_from_pc,
        caption="来自计算机文件的图像"
    )
    file_ids.append(result.photo[-1].file_id)

    # 通过链接发送文件
    image_from_url = URLInputFile("https://picsum.photos/seed/groosha/400/300")
    result = await message.answer_photo(
        image_from_url,
        caption="链接中的图像"
    )
    file_ids.append(result.photo[-1].file_id)
    await message.answer("已发送的文件：\n"+"\n".join(file_ids))


@dp.message(Command("album"))
async def cmd_album(message: Message):
    album_builder = MediaGroupBuilder(
        caption="未来相册的一般标题"
    )
    album_builder.add(
        type="photo",
        media=FSInputFile("image_from_pc.jpg")
        # caption="特定媒体的标题"

    )
    # 如果我们提前知道类型，那么代替通用 add
    # 可以直接调用 add_<type>
    album_builder.add_photo(
        # 对于链接或 file_id，可以直接指定值
        media="https://picsum.photos/seed/groosha/400/300"
    )
    album_builder.add_photo(
        media="<ваш file_id>"
    )
    await message.answer_media_group(
        # 不要忘记调用 build()
        media=album_builder.build()
    )


@dp.message(F.text)
async def extract_data(message: Message):
    data = {
        "url": "<N/A>",
        "email": "<N/A>",
        "code": "<N/A>"
    }
    entities = message.entities or []
    for item in entities:
        if item.type in data.keys():
            # 错误的方式
            # data[item.type] = message.text[item.offset : item.offset+item.length]
            # 正确的方式
            data[item.type] = item.extract_from(message.text)
    await message.reply(
        "这是我找到的：\n"
        f"URL：{html.quote(data['url'])}\n"
        f"电子邮件：{html.quote(data['email'])}\n"
        f"密码：{html.quote(data['code'])}"
    )


# 这个处理程序被上面的处理程序覆盖，
# 注释掉那个以使这个工作
@dp.message(F.text)
async def echo_with_time(message: Message):
    # 获取电脑时区中的当前时间
    time_now = datetime.now().strftime('%H:%M')
    # 创建带下划线的文本
    added_text = html.underline(f"创建于 {time_now}")
    # 发送带有添加文本的新消息
    await message.answer(f"{message.html_text}\n\n{added_text}")


@dp.message(F.animation)
async def echo_gif(message: Message):
    await message.reply_animation(message.animation.file_id)


@dp.message(F.photo)
async def download_photo(message: Message, bot: Bot):
    await bot.download(
        message.photo[-1],
        destination=f"/tmp/{message.photo[-1].file_id}.jpg"
    )


@dp.message(F.sticker)
async def download_sticker(message: Message, bot: Bot):
    await bot.download(
        message.sticker,
        destination=f"/tmp/{message.sticker.file_id}.webp"
    )


@dp.message(F.new_chat_members)
async def somebody_added(message: Message):
    for user in message.new_chat_members:
        await message.reply(f"你好，{user.full_name}")


async def main():
    # 启动机器人并跳过所有累积的传入消息
    # 是的，即使您使用的是长轮询，也可以调用此方法
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

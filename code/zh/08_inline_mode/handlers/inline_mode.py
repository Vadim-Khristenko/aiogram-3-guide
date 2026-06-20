from typing import Optional

from aiogram import Router, F, html
from aiogram.types import InlineQuery, \
    InlineQueryResultArticle, InputTextMessageContent, \
    InlineQueryResultCachedPhoto

from storage import get_links_by_id, get_images_by_id

router = Router()


@router.inline_query(F.query == "links")
async def show_user_links(inline_query: InlineQuery):
    # 此函数仅组合文本
    # 当点击内联模式中的选项时将发送的文本
    def get_message_text(
            link: str,
            title: str,
            description: Optional[str]
    ) -> str:
        text_parts = [f'{html.bold(html.quote(title))}']
        if description:
            text_parts.append(html.quote(description))
        text_parts.append("")  # 添加空行
        text_parts.append(link)
        return "\n".join(text_parts)

    results = []
    for link, link_data in get_links_by_id(inline_query.from_user.id).items():
        # 将每条记录放入结果数组
        results.append(InlineQueryResultArticle(
            id=link,  # 链接是唯一的，所以不会有问题
            title=link_data["title"],
            description=link_data["description"],
            input_message_content=InputTextMessageContent(
                message_text=get_message_text(
                    link=link,
                    title=link_data["title"],
                    description=link_data["description"]
                ),
                parse_mode="HTML"
            ),
        ))
    # 重要：必须指定 is_personal=True！
    await inline_query.answer(
        results, is_personal=True,
        switch_pm_text="添加更多 »»",
        switch_pm_parameter="add"
    )


@router.inline_query(F.query == "images")
async def show_user_images(inline_query: InlineQuery):
    results = []
    for index, file_id in enumerate(get_images_by_id(inline_query.from_user.id)):
        # 将每条记录放入结果数组
        results.append(InlineQueryResultCachedPhoto(
            id=str(index),  # 链接是唯一的，所以不会有问题
            photo_file_id=file_id
        ))
    # 重要：必须指定 is_personal=True！
    await inline_query.answer(
        results, is_personal=True,
        switch_pm_text="添加更多 »»",
        switch_pm_parameter="add"
    )

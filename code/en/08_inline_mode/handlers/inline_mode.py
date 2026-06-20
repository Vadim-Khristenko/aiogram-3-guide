from typing import Optional

from aiogram import Router, F, html
from aiogram.types import InlineQuery, \
    InlineQueryResultArticle, InputTextMessageContent, \
    InlineQueryResultCachedPhoto

from storage import get_links_by_id, get_images_by_id

router = Router()


@router.inline_query(F.query == "links")
async def show_user_links(inline_query: InlineQuery):
    # This function just collects the text that will be
    # sent when clicking on an option in inline mode
    def get_message_text(
            link: str,
            title: str,
            description: Optional[str]
    ) -> str:
        text_parts = [f'{html.bold(html.quote(title))}']
        if description:
            text_parts.append(html.quote(description))
        text_parts.append("")  # add an empty line
        text_parts.append(link)
        return "\n".join(text_parts)

    results = []
    for link, link_data in get_links_by_id(inline_query.from_user.id).items():
        # We add each entry to the final array
        results.append(InlineQueryResultArticle(
            id=link,  # links are unique, so there will be no problems
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
    # It is important to specify is_personal=True!
    await inline_query.answer(
        results, is_personal=True,
        switch_pm_text="Add more »»",
        switch_pm_parameter="add"
    )


@router.inline_query(F.query == "images")
async def show_user_images(inline_query: InlineQuery):
    results = []
    for index, file_id in enumerate(get_images_by_id(inline_query.from_user.id)):
        # We add each entry to the final array
        results.append(InlineQueryResultCachedPhoto(
            id=str(index),  # links are unique, so there will be no problems
            photo_file_id=file_id
        ))
    # It is important to specify is_personal=True!
    await inline_query.answer(
        results, is_personal=True,
        switch_pm_text="Add more »»",
        switch_pm_parameter="add"
    )

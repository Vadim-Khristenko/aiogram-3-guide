from aiogram import Router, F
from aiogram.types import InlineQuery, \
    InlineQueryResultArticle, InputTextMessageContent

router = Router()


def get_fake_results(start_num: int, size: int = 50) -> list[int]:
    """
    Generates a list of sequential numbers

    :param start_num: starting number for the generator
    :param size: batch size (default 50)
    :return: list of sequential numbers
    """
    overall_items = 195
    # If there are no more results, send an empty list
    if start_num >= overall_items:
        return []
    # Sending incomplete batch (last one)
    elif start_num + size >= overall_items:
        return list(range(start_num, overall_items+1))
    else:
        return list(range(start_num, start_num+size))


@router.inline_query(F.query == "long")
async def pagination_demo(
        inline_query: InlineQuery,
):
    # Calculate offset as a number
    offset = int(inline_query.offset) if inline_query.offset else 1
    results = [InlineQueryResultArticle(
        id=str(item_num),
        title=f"Item #{item_num}",
        input_message_content=InputTextMessageContent(
            message_text=f"Item #{item_num}"
        )
    ) for item_num in get_fake_results(offset)]
    if len(results) < 50:
        await inline_query.answer(
            results, is_personal=True
        )
    else:
        await inline_query.answer(
            results, is_personal=True,
            next_offset=str(offset+50)
        )

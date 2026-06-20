from aiogram import Router, F
from aiogram.types import InlineQuery, \
    InlineQueryResultArticle, InputTextMessageContent

router = Router()


def get_fake_results(start_num: int, size: int = 50) -> list[int]:
    """
    生成连续数字列表

    :param start_num: 生成器的起始数字
    :param size: 批次大小（默认 50）
    :return: 连续数字列表
    """
    overall_items = 195
    # 如果没有更多结果，发送空列表
    if start_num >= overall_items:
        return []
    # 发送不完整批次（最后一批）
    elif start_num + size >= overall_items:
        return list(range(start_num, overall_items+1))
    else:
        return list(range(start_num, start_num+size))


@router.inline_query(F.query == "long")
async def pagination_demo(
        inline_query: InlineQuery,
):
    # 将 offset 计算为数字
    offset = int(inline_query.offset) if inline_query.offset else 1
    results = [InlineQueryResultArticle(
        id=str(item_num),
        title=f"对象 #{item_num}",
        input_message_content=InputTextMessageContent(
            message_text=f"对象 #{item_num}"
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

from aiogram import Router, F
from aiogram.types import InlineQuery, \
    InlineQueryResultArticle, InputTextMessageContent

router = Router()


def get_fake_results(start_num: int, size: int = 50) -> list[int]:
    """
    Генерує список з послідовних чисел

    :param start_num: стартове число для генератора
    :param size: розмір пачки (за замовч. 50)
    :return: список послідовних чисел
    """
    overall_items = 195
    # Якщо результатів більше немає, відправляємо порожній список
    if start_num >= overall_items:
        return []
    # Відправка неповної пачки (останньої)
    elif start_num + size >= overall_items:
        return list(range(start_num, overall_items+1))
    else:
        return list(range(start_num, start_num+size))


@router.inline_query(F.query == "long")
async def pagination_demo(
        inline_query: InlineQuery,
):
    # Обчислюємо offset як число
    offset = int(inline_query.offset) if inline_query.offset else 1
    results = [InlineQueryResultArticle(
        id=str(item_num),
        title=f"Об'єкт №{item_num}",
        input_message_content=InputTextMessageContent(
            message_text=f"Об'єкт №{item_num}"
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

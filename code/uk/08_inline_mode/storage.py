from typing import Optional

# У реальному житті тут повинна бути нормальна СУБД.
# Але для прикладу нам буде достатньо показати на звичайному словнику.
# Врахуйте, що він скидається при перезапуску бота.
data = dict()


def add_link(
        telegram_id: int,
        link: str,
        title: str,
        description: Optional[str]
):
    """
    Зберігає посилання в словник

    :param telegram_id: ID користувача в Telegram
    :param link: текст посилання
    :param title: заголовок посилання
    :param description: (опціонально) опис посилання
    """
    data.setdefault(telegram_id, dict())
    data[telegram_id].setdefault("links", dict())
    data[telegram_id]["links"][link] = {
        "title": title,
        "description": description
    }


def add_photo(
        telegram_id: int,
        photo_file_id: str,
        photo_unique_id: str
):
    """
    Зберігає зображення в словник

    :param telegram_id: ID користувача в Telegram
    :param photo_file_id: file_id зображення
    :param photo_unique_id: file_unique_id зображення
    """
    data.setdefault(telegram_id, dict())
    data[telegram_id].setdefault("images", [])
    if photo_file_id not in data[telegram_id]["images"]:
        data[telegram_id]["images"].append((photo_file_id, photo_unique_id))


def get_links_by_id(telegram_id: int) -> dict:
    """
    Отримує збережені посилання користувача

    :param telegram_id: ID користувача в Telegram
    :return: якщо по користувачу є дані, то словник з посиланнями
    """
    if telegram_id in data and "links" in data[telegram_id]:
        return data[telegram_id]["links"]
    return dict()


def get_images_by_id(telegram_id: int) -> list[str]:
    """
    Отримує збережені зображення користувача

    :param telegram_id: ID користувача в Telegram
    :return:
    """
    if telegram_id in data and "images" in data[telegram_id]:
        return [item[0] for item in data[telegram_id]["images"]]
    return []


def delete_link(telegram_id: int, link: str):
    """
    Видаляє посилання

    :param telegram_id: ID користувача в Telegram
    :param link: посилання
    """
    if telegram_id in data:
        if "links" in data[telegram_id]:
            if link in data[telegram_id]["links"]:
                del data[telegram_id]["links"][link]


def delete_image(telegram_id: int, photo_file_unique_id: str):
    """
    Видаляє зображення

    :param telegram_id: ID користувача в Telegram
    :param photo_file_unique_id: file_unique_id зображення для видалення
    """
    if telegram_id in data and "images" in data[telegram_id]:
        for index, (_, unique_id) in enumerate(data[telegram_id]["images"]):
            if unique_id == photo_file_unique_id:
                data[telegram_id]["images"].pop(index)

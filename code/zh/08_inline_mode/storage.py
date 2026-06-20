from typing import Optional

# 在实际应用中，这里应该使用真正的数据库。
# 但对于本示例，普通字典就足够了。
# 请注意，机器人重启后数据会重置。
data = dict()


def add_link(
        telegram_id: int,
        link: str,
        title: str,
        description: Optional[str]
):
    """
    将链接保存到字典

    :param telegram_id: 用户的 Telegram ID
    :param link: 链接文本
    :param title: 链接标题
    :param description: （可选）链接描述
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
    将图片保存到字典

    :param telegram_id: 用户的 Telegram ID
    :param photo_file_id: 图片的 file_id
    :param photo_unique_id: 图片的 file_unique_id
    """
    data.setdefault(telegram_id, dict())
    data[telegram_id].setdefault("images", [])
    if photo_file_id not in data[telegram_id]["images"]:
        data[telegram_id]["images"].append((photo_file_id, photo_unique_id))


def get_links_by_id(telegram_id: int) -> dict:
    """
    获取用户保存的链接

    :param telegram_id: 用户的 Telegram ID
    :return: 如果用户有数据，返回链接字典
    """
    if telegram_id in data and "links" in data[telegram_id]:
        return data[telegram_id]["links"]
    return dict()


def get_images_by_id(telegram_id: int) -> list[str]:
    """
    获取用户保存的图片

    :param telegram_id: 用户的 Telegram ID
    :return:
    """
    if telegram_id in data and "images" in data[telegram_id]:
        return [item[0] for item in data[telegram_id]["images"]]
    return []


def delete_link(telegram_id: int, link: str):
    """
    删除链接

    :param telegram_id: 用户的 Telegram ID
    :param link: 链接
    """
    if telegram_id in data:
        if "links" in data[telegram_id]:
            if link in data[telegram_id]["links"]:
                del data[telegram_id]["links"][link]


def delete_image(telegram_id: int, photo_file_unique_id: str):
    """
    删除图片

    :param telegram_id: 用户的 Telegram ID
    :param photo_file_unique_id: 要删除的图片的 file_unique_id
    """
    if telegram_id in data and "images" in data[telegram_id]:
        for index, (_, unique_id) in enumerate(data[telegram_id]["images"]):
            if unique_id == photo_file_unique_id:
                data[telegram_id]["images"].pop(index)

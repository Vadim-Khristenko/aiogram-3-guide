from typing import Optional

# In real life, there should be a normal database here.
# But for this example, a regular dictionary will suffice.
# Note that it gets reset when the bot restarts.
data = dict()


def add_link(
        telegram_id: int,
        link: str,
        title: str,
        description: Optional[str]
):
    """
    Saves a link to the dictionary

    :param telegram_id: User's Telegram ID
    :param link: link text
    :param title: link title
    :param description: (optional) link description
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
    Saves an image to the dictionary

    :param telegram_id: User's Telegram ID
    :param photo_file_id: image file_id
    :param photo_unique_id: image file_unique_id
    """
    data.setdefault(telegram_id, dict())
    data[telegram_id].setdefault("images", [])
    if photo_file_id not in data[telegram_id]["images"]:
        data[telegram_id]["images"].append((photo_file_id, photo_unique_id))


def get_links_by_id(telegram_id: int) -> dict:
    """
    Gets user's saved links

    :param telegram_id: User's Telegram ID
    :return: if user has data, dictionary with links
    """
    if telegram_id in data and "links" in data[telegram_id]:
        return data[telegram_id]["links"]
    return dict()


def get_images_by_id(telegram_id: int) -> list[str]:
    """
    Gets user's saved images

    :param telegram_id: User's Telegram ID
    :return:
    """
    if telegram_id in data and "images" in data[telegram_id]:
        return [item[0] for item in data[telegram_id]["images"]]
    return []


def delete_link(telegram_id: int, link: str):
    """
    Deletes a link

    :param telegram_id: User's Telegram ID
    :param link: link
    """
    if telegram_id in data:
        if "links" in data[telegram_id]:
            if link in data[telegram_id]["links"]:
                del data[telegram_id]["links"][link]


def delete_image(telegram_id: int, photo_file_unique_id: str):
    """
    Deletes an image

    :param telegram_id: User's Telegram ID
    :param photo_file_unique_id: file_unique_id of image to delete
    """
    if telegram_id in data and "images" in data[telegram_id]:
        for index, (_, unique_id) in enumerate(data[telegram_id]["images"]):
            if unique_id == photo_file_unique_id:
                data[telegram_id]["images"].pop(index)

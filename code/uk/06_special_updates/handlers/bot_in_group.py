from aiogram import F, Router, Bot
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER, ADMINISTRATOR
from aiogram.types import ChatMemberUpdated

router = Router()
router.my_chat_member.filter(F.chat.type.in_({"group", "supergroup"}))

chats_variants = {
    "group": "групу",
    "supergroup": "супергрупу"
}


# Не вдалося відтворити випадок додавання бота як Restricted,
# тому прикладу з ним не буде


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> ADMINISTRATOR
    )
)
async def bot_added_as_admin(event: ChatMemberUpdated):
    # Найпростіший випадок: бот додан як адмін.
    # Легко можемо надіслати повідомлення
    await event.answer(
        text=f"Привіт! Дякую, що додали мене в "
             f'{chats_variants[event.chat.type]} "{event.chat.title}"'
             f"як адміністратора. ID чату: {event.chat.id}"
    )


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> MEMBER
    )
)
async def bot_added_as_member(event: ChatMemberUpdated, bot: Bot):
    # Варіант складніший: бота додали як звичайного учасника.
    # Але може бути відсутнім право написання повідомлень, тому заздалегідь перевіримо.
    chat_info = await bot.get_chat(event.chat.id)
    if chat_info.permissions.can_send_messages:
        await event.answer(
            text=f"Привіт! Дякую, що додали мене в "
                 f'{chats_variants[event.chat.type]} "{event.chat.title}"'
                 f"як звичайного учасника. ID чату: {event.chat.id}"
        )
    else:
        print("Якось логуємо цю ситуацію")

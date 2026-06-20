from aiogram import F, Router, Bot
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER, ADMINISTRATOR
from aiogram.types import ChatMemberUpdated

router = Router()
router.my_chat_member.filter(F.chat.type.in_({"group", "supergroup"}))

chats_variants = {
    "group": "群组",
    "supergroup": "超级群组"
}


# 无法重现将机器人添加为受限成员的情况，
# 因此将没有这种情况的示例


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> ADMINISTRATOR
    )
)
async def bot_added_as_admin(event: ChatMemberUpdated):
    # 最简单的情况：机器人被添加为管理员。
    # 我们可以轻松发送消息
    await event.answer(
        text=f"你好！谢谢你将我添加到 "
             f'{chats_variants[event.chat.type]} "{event.chat.title}"'
             f"作为管理员。群组 ID：{event.chat.id}"
    )


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> MEMBER
    )
)
async def bot_added_as_member(event: ChatMemberUpdated, bot: Bot):
    # 更复杂的情况：机器人被添加为普通成员。
    # 但可能没有发送消息的权限，所以我们先检查一下。
    chat_info = await bot.get_chat(event.chat.id)
    if chat_info.permissions.can_send_messages:
        await event.answer(
            text=f"你好！谢谢你将我添加到 "
                 f'{chats_variants[event.chat.type]} "{event.chat.title}"'
                 f"作为普通成员。群组 ID：{event.chat.id}"
        )
    else:
        print("以某种方式记录这种情况")

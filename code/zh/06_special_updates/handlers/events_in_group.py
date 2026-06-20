from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.types import Message

router = Router()

# 实际上，你可以为路由器添加一个自定义过滤器
# 检查调用者的 ID 是否在 admins 集合中。
# 然后路由器中的所有处理器都会自动只为 admins 中的人调用，
# 这会减少代码并省去不必要的 if
# 但为了清晰起见，我们将通过 if-else 来做，以便更直观


@router.message(Command("ban"), F.reply_to_message)
async def cmd_ban(message: Message, admins: set[int]):
    if message.from_user.id not in admins:
        await message.answer("您没有足够的权限来执行此操作")
    else:
        await message.chat.ban(
            user_id=message.reply_to_message.from_user.id
        )
        await message.answer("违规者已被禁言")

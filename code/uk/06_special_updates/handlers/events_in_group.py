from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.types import Message

router = Router()

# Насправді, можна на роутер навісити кастомний фільтр
# з перевіркою, лежить ли ID того, хто викликає, у множині admins.
# Тоді всі хендлери в роутері автоматично будуть викликатися
# тільки для людей з admins, це скоротить код та позбавить від зайвого if
# Але для прикладу зробимо через if-else, щоб було наочніше


@router.message(Command("ban"), F.reply_to_message)
async def cmd_ban(message: Message, admins: set[int]):
    if message.from_user.id not in admins:
        await message.answer("У вас недостатньо прав для виконання цієї дії")
    else:
        await message.chat.ban(
            user_id=message.reply_to_message.from_user.id
        )
        await message.answer("Порушник заблокований")

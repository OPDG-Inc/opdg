from aiogram.types import Message
from aiogram.filters import BaseFilter

from src.database.requests import is_user_not_exists


class IsNotExists(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        result = await is_user_not_exists(telegram_id=message.from_user.id)
        return result

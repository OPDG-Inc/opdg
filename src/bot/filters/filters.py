from aiogram.types import Message
from aiogram.filters import BaseFilter

from src.database.requests import (is_jury, is_user, is_video_status_uploaded)


class IsJury(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        result = await is_jury(telegram_id=message.from_user.id)
        return result


class IsUser(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        result = await is_user(telegram_id=message.from_user.id)
        return result


class IsVideoUploaded(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        result = await is_video_status_uploaded(telegram_id=message.from_user.id)
        return result

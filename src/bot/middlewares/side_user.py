from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.database.requests import is_user, is_jury


class SkipSideUser(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = data["event_from_user"]
        is_user_res = await is_user(user.id)
        is_jury_res = await is_jury(user.id)
        if is_user_res and is_jury_res:
            return await handler(event, data)
        print(f"какой-то рандомный чел")
        return

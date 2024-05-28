import uuid
from typing import Optional, List

from fastapi_users import schemas
from pydantic import BaseModel


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class TelegramConfScheme(BaseModel):
    telegram_grabber_api_id: Optional[int] = None
    telegram_grabber_api_hash: Optional[str] = None
    telegram_grabber_app_name: Optional[str] = None
    telegram_grabber_conf: dict

import re
import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, InvalidPasswordException, exceptions
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from helpers.db import get_user_db
from models.models import User
from helpers.itsdangerous import create_safe_token
from config import settings


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.user_auth_secret
    verification_token_secret = settings.user_auth_secret

    async def on_after_register(self, user: User, request: Optional[Request] = None):

        try:
            await self.request_verify(user, request)
        except (
            exceptions.UserNotExists,
            exceptions.UserInactive,
            exceptions.UserAlreadyVerified,
        ):
            pass

        return None

        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        reset_pass_token = create_safe_token(unsafe_string=f"{token} {user.id}")
        reset_pass_url = f"{settings.app_url}/users/reset-password/{reset_pass_token}"

        # TODO: for internationalization - we must keep this txt messages in the right place
        send_email

        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ):

        email_verify_token = create_safe_token(unsafe_string=f"{token} {user.id}")
        email_verify_url = f"{settings.app_url}/auth/jwt/verify/{email_verify_token}"

        # TODO: for internationalization - we must keep this txt messages in the right place
        # send_email

        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def validate_password(
            self, password, user
    ) -> None:
        """
        Validate a password.

        *Overloaded method*

        :param password: The password to validate.
        :param user: The user associated to this password.
        :raises InvalidPasswordException: The password is invalid.
        :return: None if the password is valid.
        """
        if not (8 <= len(password)):
            raise InvalidPasswordException("Password must be bigger than 8 symbols")

        if not re.search(r"[a-z]", password):
            raise InvalidPasswordException("Password must contain at least one lowercase letter.")

        if not re.search(r"[A-Z]", password):
            raise InvalidPasswordException("Password must contain at least one uppercase letter.")

        if not re.search(r"\d", password):
            raise InvalidPasswordException("Password must contain at least one digit.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise InvalidPasswordException("Password must contain at least one special symbol.")

        return


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.user_auth_secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)

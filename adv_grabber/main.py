import logging
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi import APIRouter
from fastapi_users import BaseUserManager, models, exceptions
from fastapi_users.router import ErrorCode
from starlette.staticfiles import StaticFiles
from config import settings
from telegram_client.tool import TelegramChatGrabber
from models.schemas import UserRead, UserUpdate, UserCreate
from helpers.itsdangerous import get_from_token
from helpers.db import get_async_session
from helpers.users import fastapi_users, auth_backend, current_active_user, get_jwt_strategy, get_user_manager
from models.models import User
import aioconsole
from qrcode import QRCode
import qrcode

server_api = FastAPI()
users_router = APIRouter()
login_router = APIRouter()
companies_router = APIRouter()
telegram_grabber_tool = TelegramChatGrabber()


logger = logging.getLogger("server")
templates = Jinja2Templates(directory="templates")



origins = [
    "*",
]

server_api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

server_api.mount("/filestorage", StaticFiles(directory="filestorage"), name="filestorage")


@server_api.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('favicon.ico')


@server_api.get("/")
async def root():
    return {"ok": "Hello!"}


@login_router.get("/refresh_token")
async def refresh_token(
        strategy=Depends(get_jwt_strategy),
        user: User = Depends(current_active_user)
):
    # TODO: update the local db
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )

    response = await auth_backend.login(strategy, user)

    return response


@login_router.get("/verify/{token}")
async def verify_user_email(
        token: str,
        db=Depends(get_async_session),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):

    email_verify_token = get_from_token(token=token)
    vt, user_id = email_verify_token.split(' ')

    db_user = await db.get(User, user_id)

    if db_user is None or not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )

    try:
        user = await user_manager.verify(token=vt)
    except (exceptions.InvalidVerifyToken, exceptions.UserNotExists):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
        )
    except exceptions.UserAlreadyVerified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED,
        )

    return {"ok": "verified"}

server_api.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
server_api.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
server_api.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
server_api.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
server_api.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@server_api.get('/start_telegram_grabber')
async def authenticated_route(user: User = Depends(current_active_user)):
    report_file = await telegram_grabber_tool.get_messages()
    return {"report_file": f"{settings.app_url}/{report_file}.csv"}


@server_api.get('/telegram_grabber_create_session')
async def telegram_create_session(user: User = Depends(current_active_user)):
    await telegram_grabber_tool.client.connect()
    qr_login = await telegram_grabber_tool.client.qr_login()
    try:
        generate_qr_code(qr_login.url)

    except AttributeError:
        pass

    return FileResponse('filestorage/telegram_grabber_tool_qrcode.png')

server_api.include_router(login_router, prefix="/auth/jwt", tags=["auth"])
server_api.include_router(users_router, prefix="/users", tags=["users"])


def generate_qr_code(token: str):
    img = qrcode.make(token)
    img.save('filestorage/telegram_grabber_tool_qrcode.png')


@server_api.on_event("startup")
async def init_client() -> None:
    pass


if __name__ == "__main__":
    """
        1. Run with Gunicorn
            gunicorn -c gunicorn_conf.py
        2. Run by Uvicorn
            uvicorn main:server_api &> logs.log &
            disown
    """

    uvicorn.run("main:server_api",
                host="127.0.0.1",
                port=3000,
                log_level="debug",
                reload=True)

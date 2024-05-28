import logging
import os
import uuid
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi import APIRouter
from fastapi_users import BaseUserManager, models, exceptions
from fastapi_users.router import ErrorCode
from fastapi_utilities import repeat_at, repeat_every
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from config import settings
from telegram_client.tool import TelegramChatGrabber
from models.schemas import UserRead, UserUpdate, UserCreate, TelegramConfScheme
from helpers.itsdangerous import get_from_token
from helpers.db import get_async_session, get_user_db
from helpers.users import fastapi_users, auth_backend, current_active_user, get_jwt_strategy, get_user_manager
from models.models import User, Configuration
import aioconsole
from qrcode import QRCode
import qrcode

server_api = FastAPI()
users_router = APIRouter()
login_router = APIRouter()
companies_router = APIRouter()
telegram_grabber_tools = dict()

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

server_api.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
# Do not announce the register router
server_api.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


async def get_telegram_grabber_tool(db, user_id: uuid.UUID):
    if telegram_grabber_tools.get(user_id):
        telegram_grabber_tool = telegram_grabber_tools[user_id]
        return telegram_grabber_tool

    telegram_grabber_tools[user_id] = TelegramChatGrabber()
    await telegram_grabber_tools[user_id].user_instance(db=db, user_id=user_id)
    telegram_grabber_tool = telegram_grabber_tools[user_id]

    return telegram_grabber_tool


async def get_tel_messages(db, user_id: uuid.UUID):
    telegram_grabber_tool = await get_telegram_grabber_tool(db=db, user_id=user_id)
    report_file = await telegram_grabber_tool.get_messages()


@server_api.get('/start_telegram_grabber')
async def start_telegram_grabber(
        background_tasks: BackgroundTasks,
        db=Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    background_tasks.add_task(get_tel_messages, db=db, user_id=user.id)
    return HTMLResponse(status_code=202)


@server_api.get('/telegram_grabber_create_session')
async def telegram_create_session(
        db=Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    telegram_grabber_tool = await get_telegram_grabber_tool(db=db, user_id=user.id)

    await telegram_grabber_tool.client.connect()
    is_authorized = await telegram_grabber_tool.client.is_user_authorized()
    if is_authorized:
        return {}

    qr_login = await telegram_grabber_tool.client.qr_login()
    try:
        generate_qr_code(qr_login.url)

    except AttributeError:
        pass

    return FileResponse('filestorage/telegram_grabber_tool_qrcode.png')


@server_api.patch('/telegram_user_configuration', response_model=dict)
async def telegram_update_config(
        telegram_config: TelegramConfScheme,
        db=Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    orm_config = await Configuration.update(db=db, user_id=user.id, config=telegram_config)

    return {}


@server_api.get("/csv_reports")
def get_csv_reports(
        user: User = Depends(current_active_user)
):

    files = os.listdir("./filestorage/csv_reports")
    files_paths = sorted([f"{settings.app_url}/filestorage/csv_reports/{f}" for f in files])

    return {"csv_reports": files_paths}


def generate_qr_code(token: str):
    img = qrcode.make(token)
    img.save('filestorage/telegram_grabber_tool_qrcode.png')


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

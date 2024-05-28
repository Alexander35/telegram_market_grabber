import os
import re
import time
import uuid
from datetime import datetime
from pathlib import Path
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
from pytimeparse import parse
import csv
from helpers.db import get_async_session
from models.models import Configuration
from config import settings


class TelegramChatGrabber:
    def __init__(self):
        self.config = None
        self.client = None
        self.db = None

    async def user_instance(self, db, user_id: uuid.UUID):
        self.db = db
        self.config = await Configuration.get_by_user(db=self.db, user_id=user_id)
        TelegramChatGrabber.create_dir(name=f"./telegram_client_session/")
        self.client = TelegramClient(
            f'./telegram_client_session/{self.config.telegram_grabber_app_name}.session',
            self.config.telegram_grabber_api_id,
            self.config.telegram_grabber_api_hash
        )

    async def send_message(self, username: str, message: str):
        entity = await self.client.get_entity(username)
        await self.client.send_message(entity=entity, message=message)

    def create_csv(self, name, records: list):
        with open(f'{name}.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.config.telegram_grabber_conf['csv_headers'])
            writer.writeheader()

            for record in records:
                writer.writerow(record)

    @staticmethod
    def create_dir(name):
        Path(f"{name}").mkdir(parents=True, exist_ok=True)

    @staticmethod
    def files_list(folder):
        files = ""
        for path in os.listdir(folder):
            if os.path.isfile(os.path.join(folder, path)):
                files = files + " " + f'{settings.app_url}/{folder}/{path}'

        return files

    async def messages(self):
        t = time.time()
        csv_records = []
        for chat in self.config.telegram_grabber_conf['chats']:

            chat_folder_name = chat['name'].split('/')[-1]
            full_folder_name = f"{settings.telegram_grabber_files_folder}/{chat_folder_name}"
            TelegramChatGrabber.create_dir(name=full_folder_name)

            async for message in self.client.iter_messages(
                    chat['name'],
                    offset_date=t - parse(chat['time_shift']),
                    reverse=True
            ):
                if not message.text:
                    continue

                user_info = await self.client(GetFullUserRequest(message.sender))

                if not user_info.users[0].username or user_info.users[0].deleted or user_info.users[0].scam or user_info.users[0].fake:
                    continue

                csv_record = {
                    "link_text": f"{chat['name']}/{message.id}",
                    "picture_list_image": [],
                    "tg_text": f"@{user_info.users[0].username}",
                    "description_text": re.sub('[,.?!\t\n ]+', ' ', message.text),
                }

                TelegramChatGrabber.create_dir(name=f"{full_folder_name}/{message.id}")
                await self.client.download_media(message=message, file=f"{full_folder_name}/{message.id}/")

                msg_files = TelegramChatGrabber.files_list(folder=f"{full_folder_name}/{message.id}")
                csv_record["picture_list_image"] = msg_files
                csv_records.append(csv_record)

        timestamp = time.time()
        timestamp_str = datetime.fromtimestamp(timestamp)
        TelegramChatGrabber.create_dir(name=f"{settings.telegram_grabber_files_folder}/csv_reports")
        report_filename = f"{settings.telegram_grabber_files_folder}/csv_reports/csv_report_{timestamp_str.strftime('%Y-%m-%d-%H-%M-%S')}"
        self.create_csv(
            name=report_filename,
            records=csv_records
        )

        await self.send_message(
            username=self.config.telegram_grabber_conf['send_reports_to'],
            message=f'Your report is ready\n{settings.app_url}/{report_filename}.csv'
        )

        return report_filename

    async def get_messages(self):
        """get text and photos and user info link to a message"""
        async with self.client:
            return await self.messages()

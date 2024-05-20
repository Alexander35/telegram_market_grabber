import os
import re
import time
import uuid
from pathlib import Path
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
from pytimeparse import parse
import csv
from config import settings


class TelegramChatGrabber:
    def __init__(self):
        self.client = TelegramClient(
            settings.telegram_grabber_conf['app_name'],
            settings.telegram_grabber_api_id,
            settings.telegram_grabber_api_hash
        )

    @staticmethod
    def create_csv(name, records: list):
        with open(f'{name}.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=settings.telegram_grabber_conf['csv_headers'])
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
        for chat in settings.telegram_grabber_conf['chats']:

            chat_folder_name = chat['name'].split('/')[-1]
            full_folder_name = f"{settings.telegram_grabber_conf['files_folder']}/{chat_folder_name}"
            TelegramChatGrabber.create_dir(name=full_folder_name)

            async for message in self.client.iter_messages(
                    chat['name'],
                    offset_date=t - parse(chat['time_shift']),
                    reverse=True
            ):
                if not message.text:
                    continue

                user_info = await self.client(GetFullUserRequest(message.sender))

                # if not user_info.user.username or user_info.user.deleted or user_info.user.scam or user_info.user.fake:
                #     continue
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
                print(msg_files)
                csv_record["picture_list_image"] = msg_files
                csv_records.append(csv_record)

        report_filename = f"{settings.telegram_grabber_conf['files_folder']}/messages{time.time()}"
        TelegramChatGrabber.create_csv(
            name=report_filename,
            records=csv_records
        )

        return report_filename

    async def get_messages(self):
        """get text and photos and user info link to a message"""
        async with self.client:
            # self.client.loop.run_until_complete(self.messages())
            return await self.messages()


if __name__ == "__main__":
    tool = TelegramChatGrabber()
    tool.get_messages()




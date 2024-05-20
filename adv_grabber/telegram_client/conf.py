telegram_grabber_api_id: int
telegram_grabber_api_hash: str

telegram_grabber_conf: dict = {
    "app_name": "telegram_chat_grabber",
    "chats":
        [
            {
                "name": "https://t.me/montenegro_market",
                # "time_shift": "1 day",
                "time_shift": "1 hour"
            }
        ],
    "csv_headers": [
        "active_boolean",
        "address_geographic_address",
        "auto_boolean",
        "condition_option_condition",
        "contact_text",
        "description_text",
        "lang_text",
        "link_text",
        "name_text",
        "picture_list_image",
        "price_number",
        "tg_text"],
    "files_folder": "filestorage"
}
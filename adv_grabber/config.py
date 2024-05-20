from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_password: str
    postgres_user: str
    postgres_db: str

    itsdangerous_secret_key: str
    itsdangerous_salt: str
    itsdangerous_token_time: int

    user_auth_secret: str
    otp_time: int

    app_url: str

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

    old_otp_code_msg: str = "OTP Code Is Too Old. New One Is Created. Check Your Email"
    invalid_otp_code_msg: str = "INVALID_OTP_CODE"
    account_not_verified_msg: str = "ACCOUNT_NOT_VERIFIED"

    no_company_name_msg: str = "No Company Name Is Provided"

    @property
    def postgres_url(self):
        return f"postgresql+asyncpg://{self.postgres_user}:{quote_plus(self.postgres_password)}@advgrabberpostgres/{self.postgres_db}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


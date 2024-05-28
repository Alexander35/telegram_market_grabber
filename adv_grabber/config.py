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
    # otp_time: int

    app_url: str

    telegram_grabber_files_folder: str

    # telegram_grabber_conf: dict = {
    #     "chats":
    #         [
    #             {
    #                 "name": "https://t.me/montenegro_market",
    #                 "time_shift": "1 hour"
    #             }
    #         ],
    #     "csv_headers": [
    #         "active_boolean",
    #         "address_geographic_address",
    #         "auto_boolean",
    #         "condition_option_condition",
    #         "contact_text",
    #         "description_text",
    #         "lang_text",
    #         "link_text",
    #         "name_text",
    #         "picture_list_image",
    #         "price_number",
    #         "tg_text"]
    # }

    @property
    def postgres_url(self):
        return f"postgresql+asyncpg://{self.postgres_user}:{quote_plus(self.postgres_password)}@advgrabberpostgres/{self.postgres_db}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


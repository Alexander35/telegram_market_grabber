import uuid
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID, GUID
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, mapped_column
from models.schemas import TelegramConfScheme
from models.schemas import UserRead


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    @staticmethod
    async def get_by_email(db, email):
        async with db:
            user_query = select(User).where(User.email == email)
            user_result = await db.execute(user_query)
            (user, ) = user_result.fetchone()
        return UserRead.model_validate(user)


class Configuration(Base):
    __tablename__ = "configuration"

    id = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID)
    telegram_grabber_api_id = Column(Integer)
    telegram_grabber_api_hash = Column(String)
    telegram_grabber_conf = Column(JSONB)
    telegram_grabber_app_name = Column(String)

    @staticmethod
    async def update(db, user_id: uuid.UUID, config: TelegramConfScheme):
        current_telegram_config_query = select(Configuration).where(Configuration.user_id == user_id)
        current_telegram_config = await db.execute(current_telegram_config_query)
        current_telegram_config_ = current_telegram_config.fetchone()

        if not current_telegram_config_:
            #     Create a new one
            orm_config = Configuration(**config.dict())
            orm_config.user_id = user_id
            db.add(orm_config)

            await db.commit()
            await db.refresh(orm_config)

            return orm_config

        (current_telegram_config_, ) = current_telegram_config_

        upd_orm_config = Configuration(**config.dict())
        if upd_orm_config.telegram_grabber_api_id is not None:
            current_telegram_config_.telegram_grabber_api_id = upd_orm_config.telegram_grabber_api_id
            current_telegram_config_.telegram_grabber_api_hash = upd_orm_config.telegram_grabber_api_hash
            current_telegram_config_.telegram_grabber_app_name = upd_orm_config.telegram_grabber_app_name

        current_telegram_config_.telegram_grabber_conf = upd_orm_config.telegram_grabber_conf

        db.add(current_telegram_config_)

        await db.commit()
        return current_telegram_config_

    @staticmethod
    async def get_by_user(db, user_id: uuid.UUID):
        current_telegram_config_query = select(Configuration).where(Configuration.user_id == user_id)
        current_telegram_config = await db.execute(current_telegram_config_query)
        current_telegram_config_ = current_telegram_config.fetchone()

        if current_telegram_config_:
            (current_telegram_config_, ) = current_telegram_config_

        return current_telegram_config_


# class Advertisement(Base):
#     __tablename__ = "advertisement"
#
#
# class MediaFile(Base):
#     __tablename__ = "media_file"
#
#
# class ReportFile(Base):
#     __tablename__ = "report_file"
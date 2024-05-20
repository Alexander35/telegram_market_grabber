from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID, GUID
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass


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
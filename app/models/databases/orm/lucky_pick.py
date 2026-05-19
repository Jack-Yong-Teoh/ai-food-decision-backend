from sqlalchemy import Column, Integer, String
from app.models.databases.orm.base import Base, AuditModel


class LuckyPick(Base, AuditModel):
    __tablename__ = "lucky_picks"

    id = Column(Integer, primary_key=True)
    option_name = Column(String, nullable=False)
    description = Column(String)

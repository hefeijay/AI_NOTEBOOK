from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone, timedelta
import uuid

Base = declarative_base()

# 北京时间（UTC+8）
BEIJING_TZ = timezone(timedelta(hours=8))


def beijing_now():
    """获取北京时间"""
    return datetime.now(BEIJING_TZ).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # 关系
    notes = relationship("Note", back_populates="owner", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "createdAt": self.created_at.isoformat() + "Z" if self.created_at else ""
        }


class Note(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False, default="新笔记")
    content = Column(Text, nullable=False, default="")
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # 关系
    owner = relationship("User", back_populates="notes")

    def to_dict(self) -> dict:
        # 确保时间以ISO格式返回，并标记为UTC时间（添加Z后缀）
        # 这样前端可以正确识别为UTC时间，然后转换为北京时间
        def format_datetime(dt):
            if dt is None:
                return ""
            # 如果datetime没有时区信息，假设它是UTC时间
            if dt.tzinfo is None:
                # 添加UTC时区标记
                return dt.isoformat() + "Z"
            return dt.isoformat()
        
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "createdAt": format_datetime(self.created_at),
            "updatedAt": format_datetime(self.updated_at)
        }


import json
from sqlalchemy import Column, String, BigInteger, Boolean, Time
from database.db_setup import Base


class Chat(Base):
    __tablename__ = 'chats'

    # Уникальный идентификатор чата
    chat_id = Column(BigInteger, primary_key=True)
    chat_name = Column(String, nullable=True)  # Название чата
    default_prompt_id = Column(String, nullable=True)  # ID дефолтного промпта
    # Флаг для анализа по расписанию
    schedule_analysis = Column(Boolean, default=False)
    # Время, от которого начинается выборка сообщений (например, 05:00)
    analysis_time = Column(Time, nullable=True)
    send_time = Column(Time, nullable=True)

    def __repr__(self):
        return f"<Chat(chat_id={self.chat_id}, chat_name={self.chat_name}, default_prompt_id={self.default_prompt_id})>"

    def to_dict(self):
        return {
            "chat_id": self.chat_id,
            "chat_name": self.chat_name,
            "default_prompt_id": self.default_prompt_id,
            "schedule_analysis": self.schedule_analysis,
            "analysis_time": self.analysis_time.isoformat() if self.analysis_time else None,
            "send_time": self.send_time.isoformat() if self.send_time else None,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

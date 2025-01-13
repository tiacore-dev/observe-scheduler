from sqlalchemy import Column, String, Text, Boolean
from database.db_setup import Base


class Prompt(Base):
    __tablename__ = 'prompts'

    prompt_id = Column(String, primary_key=True)
    prompt_name = Column(String(255), nullable=False)  # Название промпта
    text = Column(Text)  # Текст промпта
    use_automatic = Column(Boolean, nullable=True,
                           default=False)  # Новый булевый столбец

    def to_dict(self):
        return {
            "prompt_id": self.prompt_id,
            "prompt_name": self.prompt_name,
            "text": self.text,
            "use_automatic": self.use_automatic  # Форматируем дату для JSON
        }

from sqlalchemy import Column, String, BigInteger
from database.db_setup import Base


class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True, autoincrement=False)
    username = Column(String)  # Имя пользователя

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username
        }

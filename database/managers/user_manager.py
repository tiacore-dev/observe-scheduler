import logging
from sqlalchemy import exists
from database.models.user import User
from database.db_globals import Session


class UserManager:
    def __init__(self):
        self.Session = Session

    def add_user(self, user_id, username=None):
        """Добавляем пользователя стандартно"""
        new_user = User(user_id=user_id, username=username)
        with self.Session() as session:
            try:
                session.add(new_user)
                session.commit()
                logging.info(f"Пользователь {user_id} успешно добавлен.")
                return user_id
            except Exception as e:
                session.rollback()
                logging.error(
                    f"Ошибка при добавлении пользователя {user_id}: {e}")
                raise

    def user_exists(self, user_id):
        """Проверка существования пользователя по ID"""
        with self.Session() as session:
            return session.query(exists().where(User.user_id == user_id)).scalar()

    def get_user_by_user_id(self, user_id):
        """Получаем пользователя по его ID"""
        with self.Session() as session:
            try:
                logging.info(
                    f"Открытие сессии для получения пользователя {user_id}")
                user = session.query(User).filter(
                    User.user_id == user_id).first()
                if user:
                    logging.info(f"Пользователь найден: {user}")
                    return user.to_dict()
                else:
                    logging.warning(f"Пользователь с ID {user_id} не найден.")
                    return None

            except Exception as e:
                logging.error(
                    f"Ошибка при получении пользователя {user_id}: {e}")
                raise

    def delete_user(self, user_id):
        """Удаление пользователя по user_id"""
        with self.Session() as session:
            try:
                user = session.query(User).filter_by(user_id=user_id).first()
                if user:
                    session.delete(user)
                    session.commit()
                    logging.info(f"Пользователь {user_id} успешно удалён.")
                    return True
                else:
                    logging.warning(f"Пользователь {user_id} не найден.")
                    return False
            except Exception as e:
                session.rollback()
                logging.error(
                    f"Ошибка при удалении пользователя {user_id}: {e}")
                raise

    def get_users(self):
        """Получаем всех пользователей"""
        with self.Session() as session:
            try:
                users = session.query(User).all()
                return users
            except Exception as e:
                logging.error(f"Ошибка при получении пользователей: {e}")
                raise

    def update_username(self, user_id, username):
        """Обновляем имя пользователя"""
        with self.Session() as session:
            try:
                user_in_db = session.query(User).filter_by(
                    user_id=user_id).first()
                if user_in_db:
                    user_in_db.username = username
                    session.commit()
                    logging.info(f"""Имя пользователя {
                                 user_id} обновлено на {username}.")
                else:
                    logging.warning(f"Пользователь {user_id} не найден.""")
            except Exception as e:
                session.rollback()
                logging.error(
                    f"Ошибка при обновлении имени пользователя {user_id}: {e}")
                raise

import uuid
import logging
from datetime import datetime
from dateutil.parser import isoparse
from database.models.messages import Message
from database.db_globals import Session


class MessageManager:
    def __init__(self):
        self.Session = Session

    def add_message(self, timestamp, user_id, chat_id, text=None, s3_key=None):
        with self.Session() as session:
            try:
                message_id = uuid.uuid4()
                message_data = Message(
                    message_id=message_id,
                    timestamp=timestamp,
                    user_id=user_id,
                    chat_id=chat_id,
                    text=text,
                    s3_key=s3_key
                )
                # Сохранение данных в базу
                session.add(message_data)
                session.commit()
                # logging.info(f"Сообщение {message_id} успешно записано в базу данных.")
            except Exception as e:
                logging.error(f"""Ошибка записи сообщения {
                              message_id} в базу данных: {e}""")
                session.rollback()

    def get_filtered_messages(self, start_date=None, end_date=None, user_id=None, chat_id=None):
        with self.Session() as session:
            query = session.query(Message)
            if start_date:
                start_date_parsed = isoparse(start_date) if isinstance(
                    start_date, str) else start_date
                query = query.filter(Message.timestamp >= start_date_parsed)
            if end_date:
                end_date_parsed = isoparse(end_date) if isinstance(
                    end_date, str) else end_date
                query = query.filter(Message.timestamp <= end_date_parsed)
            if user_id:
                query = query.filter(Message.user_id == user_id)
            if chat_id:
                query = query.filter(Message.chat_id == chat_id)
            try:
                # results = session.execute(query).scalars().all()
                results = query.all()

                return results
            except Exception as e:
                logging.error(f"Ошибка выполнения запроса: {e}")
                raise

    def get_paginated_messages(self, start_date=None, end_date=None, user_id=None, chat_id=None, limit=10, offset=0):
        with self.Session() as session:
            query = session.query(Message)
            try:
                # Фильтры
                if start_date:
                    if isinstance(start_date, str):
                        try:
                            start_date_parsed = isoparse(
                                start_date)  # Поддержка ISO-строк
                        except ValueError as e:
                            raise ValueError(f"""Некорректный формат start_date: {
                                start_date}""") from e
                    elif isinstance(start_date, datetime):
                        start_date_parsed = start_date
                    else:
                        raise ValueError(
                            "start_date должен быть строкой в формате ISO 8601 или datetime.")
                    query = query.filter(
                        Message.timestamp >= start_date_parsed)

                if end_date:
                    if isinstance(end_date, str):
                        try:
                            end_date_parsed = isoparse(
                                end_date)  # Поддержка ISO-строк
                        except ValueError as e:
                            raise ValueError(f"""Некорректный формат end_date: {
                                end_date}""") from e
                    elif isinstance(end_date, datetime):
                        end_date_parsed = end_date
                    else:
                        raise ValueError(
                            "end_date должен быть строкой в формате ISO 8601 или datetime.")
                    query = query.filter(Message.timestamp <= end_date_parsed)

                if user_id:
                    query = query.filter(Message.user_id == int(user_id))

                if chat_id:
                    query = query.filter(Message.chat_id == int(chat_id))

                # Общее количество сообщений (для пагинации)
                total_count = query.count()

                # Применяем limit и offset
                query = query.order_by(Message.timestamp.desc()
                                       ).limit(limit).offset(offset)

                return query.all(), total_count
            except Exception as e:
                logging.error(f"""Ошибка в базе данных: {e}""")

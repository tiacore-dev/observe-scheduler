from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


def init_db(database_url):
    engine = create_engine(
        database_url,
        pool_pre_ping=True,  # Проверяет соединение перед использованием
        pool_size=10,        # Размер пула
        max_overflow=20,     # Дополнительные соединения сверх пула
        echo=False,           # Отключить детальный вывод SQL
        # Таймаут в миллисекундах
        connect_args={"options": "-c statement_timeout=30000"},
        pool_timeout=30,  # Таймаут соединения в секундах
        # isolation_level="SERIALIZABLE"
        isolation_level="READ COMMITTED"
    )
    Session = sessionmaker(bind=engine)

    return engine, Session, Base

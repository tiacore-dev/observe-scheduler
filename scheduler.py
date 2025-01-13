from datetime import datetime
import logging
import os
from dotenv import load_dotenv
from pytz import timezone
import openai
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from database import set_db_globals, init_db
from utils import analyze, save_analysis_result, send_analysis_result

load_dotenv()
# Настройка таймзоны Новосибирска
novosibirsk_tz = timezone('Asia/Novosibirsk')

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Инициализация планировщика с использованием SQLAlchemy для хранения задач
scheduler = BackgroundScheduler(
    jobstores={
        # База данных SQLite для хранения задач
        'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
    },
    executors={
        'default': ThreadPoolExecutor(10),  # 10 потоков для задач
        'processpool': ProcessPoolExecutor(2)  # 2 процесса
    },
    timezone='Asia/Novosibirsk'
)


def execute_analysis(chat_id, analysis_time):
    """
    Выполняет анализ сообщений для указанного чата и отправляет результат.
    """
    try:
        # Вызов функции анализа (замените на вашу логику)
        logging.info(f"""Выполнение анализа для чата {
                     chat_id} в {analysis_time}.""")
        data = analyze(chat_id, analysis_time)
        save_analysis_result(data)
        logging.info(
            f"Анализ завершён и данные отправлены для чата {chat_id}.")
    except Exception as e:
        logging.error(f"Ошибка при выполнении анализа для чата {chat_id}: {e}")


def check_and_execute_tasks():
    """
    Проверяет задачи, запланированные на текущий час, и выполняет их.
    """
    from database.managers.chat_manager import ChatManager
    chat_manager = ChatManager()
    now = datetime.now(novosibirsk_tz)
    current_hour = now.hour

    logging.info(f"Проверка задач для выполнения в {now.strftime('%H:%M')}.")

    try:
        # Получение всех чатов с активным расписанием
        chats = chat_manager.get_all_chats()
        tasks_to_execute = [
            chat for chat in chats
            if chat.schedule_analysis and chat.analysis_time.hour == current_hour
        ]

        if tasks_to_execute:
            logging.info(
                f"Найдено {len(tasks_to_execute)} задач для выполнения.")
            for chat in tasks_to_execute:
                execute_analysis(chat.chat_id, chat.analysis_time)
        else:
            logging.info("Нет задач для выполнения в текущий час.")

    except Exception as e:
        logging.error(f"Ошибка при проверке задач: {e}")


def send_tasks():
    """
    Проверяет задачи, запланированные на текущий час, и выполняет их.
    """
    from database.managers.chat_manager import ChatManager
    from database.managers.analysis_manager import AnalysisManager

    chat_manager = ChatManager()
    analysis_manager = AnalysisManager()

    now = datetime.now(novosibirsk_tz)
    current_hour = now.hour

    logging.info(f"Проверка задач для выполнения в {now.strftime('%H:%M')}.")

    try:
        # Получение всех чатов с активным расписанием
        chats = chat_manager.get_all_chats()
        tasks_to_execute = [
            chat for chat in chats
            if chat.schedule_analysis and chat.send_time.hour == current_hour
        ]

        if tasks_to_execute:
            logging.info(
                f"Найдено {len(tasks_to_execute)} задач для выполнения.")
            for chat in tasks_to_execute:
                # Получаем результат анализа за сегодня
                analysis_result = analysis_manager.get_today_analysis(
                    chat.chat_id)

                if analysis_result:
                    send_analysis_result(chat.chat_id, analysis_result.result)
                    logging.info(f"""Результат анализа отправлен для чата {
                                 chat.chat_id}.""")
                else:
                    logging.warning(f"""Результат анализа для чата {
                                    chat.chat_id} за сегодня не найден.""")
        else:
            logging.info("Нет задач для выполнения в текущий час.")

    except Exception as e:
        logging.error(f"Ошибка при проверке задач: {e}")


def add_hourly_analysis():
    """
    Добавляет задачу, которая выполняется каждый час в указанное время.
    """
    # Добавляем новую задачу
    scheduler.add_job(
        check_and_execute_tasks,
        'cron',
        hour='*',  # Каждый час
        minute=0,  # В начале часа
        id='Analysis_schedule',
        replace_existing=True
    )
    logging.info("Добавлена задача для выполнения анализа по расписанию.")


def add_hourly_send():
    """
    Добавляет задачу, которая выполняется каждый час в указанное время.
    """
    # Добавляем новую задачу
    scheduler.add_job(
        send_tasks,
        'cron',
        hour='*',  # Каждый час
        minute=0,  # В начале часа
        id='Send_schedule',
        replace_existing=True
    )
    logging.info("Добавлена задача для выполнения анализа по расписанию.")


def start_scheduler():
    """
    Запускает планировщик и добавляет задачи для всех активных чатов из базы данных.
    """
    database_url = os.getenv('DATABASE_URL')
    engine, Session, Base = init_db(database_url)
    set_db_globals(engine, Session, Base)
    openai.api_key = os.getenv('OPENAI_API_KEY')
    add_hourly_analysis()
    add_hourly_send()
    logging.info("Все задачи добавлены в планировщик.")

    scheduler.start()
    logging.info("Планировщик успешно запущен.")


def list_scheduled_jobs():
    """
    Выводит список всех запланированных задач.
    """
    for job in scheduler.get_jobs():
        logging.info(f"Job ID: {job.id}, trigger: {job.trigger}")


def clear_existing_jobs():
    """
    Удаляет все существующие задачи из планировщика.
    """
    try:
        scheduler.remove_all_jobs()
        logging.info("Все задачи успешно удалены из планировщика.")
    except Exception as e:
        logging.error(f"Ошибка при удалении всех задач: {e}")

# from celery import app
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pytz import timezone, UTC
from telebot import TeleBot
from utils import get_chat_name


load_dotenv()

novosibirsk_tz = timezone('Asia/Novosibirsk')

BOT_TOKEN = os.getenv('TG_API_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')


def analyze(chat_id, analysis_time):
    """
    Анализирует сообщения в чате за указанный временной промежуток.
    """
    logging.info(f"Начало анализа для чата {chat_id}")
    from database.managers.chat_manager import ChatManager
    from database.managers.message_manager import MessageManager
    from utils import get_prompt
    from utils import chatgpt_analyze
    chat_manager = ChatManager()
    message_manager = MessageManager()

    chat = chat_manager.get_chat_by_id(chat_id)
    if not chat:
        logging.error(f"Чат {chat_id} не найден.")
        raise ValueError(f"Чат {chat_id} не найден.")

    now_nsk = datetime.now(novosibirsk_tz)

    # now_nsk уже timezone-aware, значит можно безопасно заменять время и отнимать дни
    analysis_start_nsk = now_nsk.replace(
        hour=analysis_time.hour,
        minute=analysis_time.minute,
        second=analysis_time.second,
        microsecond=0
    ) - timedelta(days=1)

    analysis_end_nsk = now_nsk.replace(
        hour=analysis_time.hour,
        minute=analysis_time.minute,
        second=analysis_time.second,
        microsecond=0
    )

    # оба уже имеют tzinfo, можно переводить в UTC
    analysis_start = analysis_start_nsk.astimezone(UTC)
    analysis_end = analysis_end_nsk.astimezone(UTC)

    logging.info(f"Диапазон анализа: {analysis_start} - {analysis_end}")

    try:
        messages = message_manager.get_filtered_messages(
            start_date=analysis_start.isoformat(),
            end_date=analysis_end.isoformat(),
            chat_id=chat_id
        )
    except Exception as e:
        logging.error(f"Ошибка при получении сообщений: {e}")
        raise

    filters = {
        "chat_id": chat_id,
        "start_date": analysis_start.isoformat(),
        "end_date": analysis_end.isoformat(),
        "user_id": None
    }

    if not messages:
        logging.warning(f"""Нет сообщений для анализа в чате {
                        chat_id} за период {analysis_start} - {analysis_end}.""")
        return {
            "chat_id": chat_id,
            "analysis_result": None,
            "tokens_input": 0,
            "tokens_output": 0,
            "prompt_id": chat['default_prompt_id'],
            "filters": filters
        }

    logging.info(f"Сообщений для анализа найдено: {len(messages)}")

    try:
        messages = [msg.to_dict() for msg in messages]
        prompt = get_prompt(chat['default_prompt_id'])
        if not prompt:
            raise ValueError(
                f"Промпт с ID {chat['default_prompt_id']} не найден.")

        analysis_result, tokens_input, tokens_output = chatgpt_analyze(
            prompt, messages)
    except Exception as e:
        logging.error(f"Ошибка при анализе сообщений: {e}")
        raise

    logging.info(f"Анализ завершён для чата {chat_id}.")
    return {
        "chat_id": chat_id,
        "analysis_result": analysis_result,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "prompt_id": chat['default_prompt_id'],
        "filters": filters
    }


def save_analysis_result(data):
    """
    Сохраняет результат анализа в базу данных.
    """
    logging.info(f"Сохранение результата анализа для чата {data['chat_id']}.")
    from database.managers.analysis_manager import AnalysisManager
    analysis_manager = AnalysisManager()
    if data["analysis_result"]:
        analysis_manager.save_analysis_result(
            data["prompt_id"],
            data["analysis_result"],
            data['filters'],
            data["tokens_input"],
            data["tokens_output"]
        )
        logging.info(f"Результат анализа сохранён для чата {data['chat_id']}.")
    else:
        logging.info(f"Для чата {data['chat_id']} нет анализа для сохранения.")


def send_analysis_result(chat_id, analysis_result):
    """
    Отправляет результат анализа в Telegram.
    """
    bot = TeleBot(BOT_TOKEN)

    chat = get_chat_name(chat_id)

    message_text = f"""Результат анализа для чата {
        chat}:\n\n{analysis_result}"""

    try:
        bot.send_message(chat_id=CHAT_ID, text=message_text)
        logging.info(f"""Результат анализа для чата {
                     chat_id} успешно отправлен.""")
    except Exception as e:
        logging.error(f"""Ошибка при отправке результата в Telegram для чата {
                      chat_id}: {e}""", exc_info=True)
    finally:
        bot.stop_bot()

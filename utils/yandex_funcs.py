import os
import logging
import json
import requests
from dotenv import load_dotenv
from utils import get_chat_name, get_user_name


load_dotenv()

YANDEX_GPT_API_URL = os.getenv('YANDEX_GPT_API_URL')

# Токен и ID каталога
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
FOLDER_ID = os.getenv('FOLDER_ID')


# Функция анализа текста через YandexGPT


def chatgpt_analyze(prompt, messages):
    """
    Анализирует сообщения через YandexGPT.

    :param prompt: Текст системного промпта.
    :param messages: Список сообщений (JSON).
    :return: Результат анализа.
    """
    logging.info("Начало анализа набора сообщений.")

    api_messages = []

    for msg in messages:
        if "text" in msg and msg["text"]:
            user = get_user_name(msg.get("user_id"))
            chat = get_chat_name(msg.get("chat_id"))

            message_data = {
                "user": user,
                "chat": chat,
                "timestamp": msg.get("timestamp", "Неизвестно"),
                "text": msg.get("text", "Пустое сообщение"),
            }
            api_messages.append(json.dumps(message_data, ensure_ascii=False))

    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 2000
        },
        "messages": [
            {"role": "system", "text": prompt},
            {"role": "user", "text": f"{api_messages}"}
        ]
    }

    try:
        response = requests.post(
            YANDEX_GPT_API_URL,
            headers=headers,
            json=payload,
            timeout=300
        )
        response_data = response.json()

        if "result" in response_data:
            analysis = response_data["result"]["alternatives"][0]["message"]["text"]
            return analysis, None, None  # В YandexGPT пока нет токенов
        else:
            logging.error(f"Ошибка анализа: {response_data}")
            return None, None, None
    except Exception as e:
        logging.error(f"Ошибка при вызове YandexGPT API: {e}")
        return None, None, None

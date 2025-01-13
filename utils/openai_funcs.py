import logging
import json
import openai
from utils import get_chat_name, get_user_name


def chatgpt_analyze(prompt, messages):
    """
    Запускает анализ набора сообщений через OpenAI API с возможностью отправки изображений.

    :param prompt: Текст системного промпта.
    :param messages: Список сообщений (JSON), включая ссылки на изображения.
    :return: Результат анализа и количество использованных токенов.
    """
    logging.info("Начало анализа набора сообщений.")

    api_messages = []

    for msg in messages:
        # Учитываем только сообщения с текстом
        if "text" in msg and msg["text"]:

            user = get_user_name(msg.get("user_id"))
            chat = get_chat_name(msg.get("chat_id"))

            message_data = {
                "user": user,
                "chat": chat,
                "timestamp": msg.get("timestamp", "Неизвестно"),
                "text": msg.get("text", "Пустое сообщение"),
            }
            # Добавляем сообщение как JSON
            api_messages.append(
                json.dumps(message_data, ensure_ascii=False)
            )

    logging.info("Начало проведения анализа")
    messages = [{"role": "system", "content": prompt},
                {"role": "user", "content": f"{api_messages}"}]
    try:
        # Вызов OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o",  # Убедитесь, что используете правильную модель
            messages=messages
        )
        # Получение результата анализа
        analysis = response.choices[0].message.content
        tokens_input = response.usage.prompt_tokens  # Токены на отправку
        tokens_output = response.usage.completion_tokens  # Токены на ответ

        logging.info("Анализ текста завершен.")
        return analysis, tokens_input, tokens_output

    except Exception as e:
        logging.error(f"Ошибка OpenAI API: {e}")
        raise e

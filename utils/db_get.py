import logging


def get_prompt(prompt_id):
    from database.managers.prompt_manager import PromptManager
    db = PromptManager()
    prompt = db.get_prompt_by_prompt_id(prompt_id)
    return prompt['text']


def get_prompt_name(prompt_id):
    from database.managers.prompt_manager import PromptManager
    db = PromptManager()
    prompt = db.get_prompt_by_prompt_id(prompt_id)
    return prompt['prompt_name']


def get_user_name(user_id):
    from database.managers.user_manager import UserManager
    db = UserManager()
    try:
        user = db.get_user_by_user_id(user_id)
        if user:
            return user['username']
        else:
            logging.warning(f"Пользователь с ID {user_id} не найден.")
            return None
    except Exception as e:
        logging.error(
            f"Ошибка при получении имени пользователя {user_id}: {e}")
        raise


def get_chat_name(chat_id):
    from database.managers.chat_manager import ChatManager
    db = ChatManager()
    try:
        chat = db.get_chat_by_id(chat_id)
        if chat:
            return chat['chat_name']
        else:
            logging.warning(f"Чат с ID {chat_id} не найден.")
            return None
    except Exception as e:
        logging.error(
            f"Ошибка при получении имени чата {chat_id}: {e}")
        raise

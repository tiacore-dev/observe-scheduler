import logging
import uuid
from database.models.prompt import Prompt
from database.db_globals import Session


class PromptManager:
    def __init__(self):
        self.Session = Session

    def add_prompt(self, prompt_name, text, use_automatic=False):
        """Добавляем новый промпт"""
        prompt_id = str(uuid.uuid4())
        new_prompt = Prompt(
            prompt_id=prompt_id,
            prompt_name=prompt_name,
            text=text,
            use_automatic=use_automatic
        )

        with self.Session() as session:
            try:
                session.add(new_prompt)
                session.commit()
                logging.info("Промпт успешно сохранен.")
                return prompt_id
            except Exception as e:
                session.rollback()
                logging.error(f"Ошибка при добавлении промпта: {e}")
                raise

    def get_prompts(self):
        """Получаем все промпты"""
        with self.Session() as session:
            logging.info("Получение всех промптов")
            prompts = session.query(Prompt).all()
            return [[p.prompt_name, p.text, p.prompt_id, p.use_automatic] for p in prompts]

    def get_prompt_by_prompt_id(self, prompt_id):
        """Получаем промпт по его ID"""
        with self.Session() as session:
            logging.info(f"Получение промпта по prompt_id: {prompt_id}")
            prompt = session.query(Prompt).filter_by(
                prompt_id=prompt_id).first()
            return prompt.to_dict() if prompt else None

    def get_prompt_by_prompt_name(self, prompt_name):
        """Получаем промпт по его имени"""
        with self.Session() as session:
            logging.info(f"Получение промпта по имени: {prompt_name}")
            prompt = session.query(Prompt).filter_by(
                prompt_name=prompt_name).first()
            return prompt.to_dict() if prompt else None

    def edit_prompt(self, prompt_id, new_text, new_prompt_name):
        """Редактируем существующий промпт"""
        with self.Session() as session:
            try:
                logging.info(f"Редактирование промпта '{prompt_id}'")
                prompt = session.query(Prompt).filter_by(
                    prompt_id=prompt_id).first()
                if prompt:
                    prompt.text = new_text
                    prompt.prompt_name = new_prompt_name
                    session.commit()
                    logging.info(f"Промпт '{prompt_id}' успешно обновлен.")
                    return True
                else:
                    logging.warning(f"Промпт '{prompt_id}' не найден")
                    return False
            except Exception as e:
                session.rollback()
                logging.error(f"Ошибка при редактировании промпта: {e}")
                raise

    def delete_prompt(self, prompt_id):
        """Удаляем промпт по его ID"""
        with self.Session() as session:
            try:
                logging.info(f"Удаление промпта '{prompt_id}'")
                prompt = session.query(Prompt).filter_by(
                    prompt_id=prompt_id).first()
                if prompt:
                    session.delete(prompt)
                    session.commit()
                    logging.info(f"Промпт '{prompt_id}' успешно удален.")
                else:
                    logging.warning(f"Промпт '{prompt_id}' не найден")
            except Exception as e:
                session.rollback()
                logging.error(f"Ошибка при удалении промпта: {e}")
                raise

    def get_automatic_prompt(self):
        """Получаем автоматический промпт"""
        with self.Session() as session:
            logging.info("Поиск автоматического промпта")
            prompt = session.query(Prompt).filter_by(
                use_automatic=True).first()
            if prompt:
                logging.info(f"""Автоматический промпт '{
                             prompt.prompt_name}' найден""")
                return prompt.to_dict()
            else:
                logging.info("Автоматический промпт не найден")
                return None

    def reset_automatic_flag(self):
        """Сбрасываем флаг 'use_automatic' для всех промптов"""
        with self.Session() as session:
            try:
                logging.info("Сброс флага 'use_automatic' для всех промптов")
                prompts = session.query(Prompt).filter_by(
                    use_automatic=True).all()
                for prompt in prompts:
                    prompt.use_automatic = False
                session.commit()
                logging.info("Флаг 'use_automatic' успешно сброшен.")
            except Exception as e:
                session.rollback()
                logging.error(f"Ошибка при сбросе флага 'use_automatic': {e}")
                raise

    def set_automatic_flag(self, prompt_id, use_automatic):
        """Устанавливаем флаг 'use_automatic' для указанного промпта"""
        with self.Session() as session:
            try:
                logging.info(
                    f"Установка флага 'use_automatic' для промпта ID: {prompt_id}")
                prompt = session.query(Prompt).filter_by(
                    prompt_id=prompt_id).first()
                if prompt:
                    prompt.use_automatic = use_automatic
                    session.commit()
                    logging.info(f"""Флаг 'use_automatic' для промпта ID: {
                                 prompt_id} успешно обновлён.""")
                else:
                    logging.warning(f"Промпт ID: {prompt_id} не найден.")
                    raise ValueError(f"Prompt with ID {prompt_id} not found")
            except Exception as e:
                session.rollback()
                logging.error(f"""Ошибка при установке флага 'use_automatic' для промпта ID: {
                              prompt_id}: {e}""")
                raise

    def get_all_prompts(self):
        """Получаем все промпты"""
        with self.Session() as session:
            logging.info("Получение всех промптов")
            return session.query(Prompt).all()

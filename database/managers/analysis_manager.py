import logging
import json
from datetime import datetime, timedelta
from database.models.analysis import AnalysisResult
from database.db_globals import Session
from utils.db_get import get_prompt_name


class AnalysisManager:
    def __init__(self):
        self.Session = Session

    def save_analysis_result(self, prompt_id, result_text, filters, tokens_input, tokens_output):
        """Сохраняет результат анализа."""
        with self.Session() as session:
            try:
                analysis_id = AnalysisResult().save(
                    session=session,
                    prompt_id=prompt_id,
                    result_text=result_text,
                    filters=filters,
                    tokens_input=tokens_input,
                    tokens_output=tokens_output
                )
                return analysis_id
            except Exception as e:
                logging.error(f"Ошибка при сохранении анализа: {e}")
                session.rollback()
                raise

    def get_analysis_all(self, offset=0, limit=10):
        """Получает все анализы с пагинацией."""
        with self.Session() as session:
            try:
                analyses = (
                    session.query(AnalysisResult)
                    .order_by(AnalysisResult.timestamp.desc())
                    .offset(offset)
                    .limit(limit)
                    .all()
                )
                total_count = session.query(AnalysisResult).count()
                logging.info(f"""Найдено {total_count} анализов, возвращаем {
                             len(analyses)} начиная с {offset}""")
                result = [
                    {
                        'analysis_id': analysis.analysis_id,
                        'prompt_id': analysis.prompt_id,
                        'prompt_name': get_prompt_name(analysis.prompt_id),
                        'filters': json.loads(analysis.filters) if analysis.filters else 'Не указаны',
                        'timestamp': analysis.timestamp.isoformat(),
                        'preview': analysis.result_text[:100] + '...' if len(analysis.result_text) > 100 else analysis.result_text
                    }
                    for analysis in analyses
                ]
                return {'analyses': result, 'total_count': total_count}
            except Exception as e:
                logging.error(f"Ошибка при получении анализов: {e}")
                return {'error': str(e), 'analyses': [], 'total_count': 0}

    def get_analysis_by_id(self, analysis_id):
        """Получает анализ по его ID."""
        with self.Session() as session:
            try:
                analysis = session.query(AnalysisResult).filter_by(
                    analysis_id=analysis_id).first()
                if analysis:
                    try:
                        filters = json.loads(
                            analysis.filters) if analysis.filters else None
                    except json.JSONDecodeError:
                        filters = "Некорректные данные"

                    filters_readable = (
                        ", ".join([f"{key}: {value}" for key,
                                  value in filters.items()])
                        if isinstance(filters, dict)
                        else filters
                    )

                    return {
                        'analysis_id': analysis.analysis_id,
                        'prompt_id': analysis.prompt_id,
                        'prompt_name': get_prompt_name(analysis.prompt_id),
                        'timestamp': analysis.timestamp.isoformat(),
                        'result_text': analysis.result_text,
                        'filters': filters_readable or 'Не указаны',
                        'tokens_input': analysis.tokens_input or 'Неизвестно',
                        'tokens_output': analysis.tokens_output or 'Неизвестно'
                    }
                return None
            except Exception as e:
                logging.error(f"Ошибка при получении анализа по ID: {e}")
                raise

    def get_today_analysis(self, chat_id: int):
        """
        Возвращает результат анализа для указанного chat_id, проведённого сегодня.
        """
        with self.Session() as session:
            # Используем UTC для корректной работы с датами
            today = datetime.utcnow().date()
            tomorrow = today + timedelta(days=1)

            return (
                session.query(AnalysisResult)
                # Фильтр по chat_id внутри filters
                .filter(AnalysisResult.filters.op("->>")("chat_id") == str(chat_id))
                # Анализы, выполненные с начала сегодняшнего дня
                .filter(AnalysisResult.timestamp >= today)
                # До начала завтрашнего дня
                .filter(AnalysisResult.timestamp < tomorrow)
                # Последний результат за сегодня
                .order_by(AnalysisResult.timestamp.desc())
                .first()
            )

import logging
import json
from datetime import datetime, timedelta
from pytz import timezone, UTC
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

    def get_today_analysis(self, chat_id):
        """
        Возвращает результат анализа для указанного chat_id, проведённого за последние 24 часа по Новосибирскому времени.
        """
        with self.Session() as session:
            # Текущее время в Новосибирске
            novosibirsk_tz = timezone('Asia/Novosibirsk')
            now_nsk = datetime.now(novosibirsk_tz)

            # Начало периода за последние 24 часа в Новосибирском времени
            last_24_hours_start_nsk = now_nsk - timedelta(days=1)

            # Конвертация диапазона в UTC
            last_24_hours_start_utc = last_24_hours_start_nsk.astimezone(UTC)
            now_utc = now_nsk.astimezone(UTC)

            # Извлекаем все записи за последние 24 часа (UTC)
            results = (
                session.query(AnalysisResult)
                .filter(AnalysisResult.timestamp >= last_24_hours_start_utc)
                .filter(AnalysisResult.timestamp < now_utc)
                .order_by(AnalysisResult.timestamp.desc())
                .all()
            )
            if results:
                # Фильтруем записи в памяти
                for result in results:
                    try:
                        filters = json.loads(
                            result.filters) if result.filters else {}
                        if filters.get("chat_id") == str(chat_id):
                            return result
                    except json.JSONDecodeError:
                        logging.error(f"""Некорректный JSON в поле filters: {
                            result.filters}""")
            else:
                return None  # Если ни одна запись не соответствует

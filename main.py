import logging
import time
from scheduler import start_scheduler, scheduler

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_scheduler()
    try:
        while True:
            time.sleep(1)  # Оставляем приложение запущенным
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logging.info("Планировщик остановлен.")

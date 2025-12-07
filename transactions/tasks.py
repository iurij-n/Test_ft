import time
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError


@shared_task(bind=True, max_retries=3, default_retry_delay=3)
def send_notification_task(self, user_id: str, amount):
    try:
        print(f"[{time.strftime('%H:%M:%S')}] Попытка отправить уведомление пользователю {user_id} на сумму {amount}")
        time.sleep(5)
        raise Exception("Telegram API временно недоступен")   # ← симуляция ошибки
    except Exception as exc:
        if self.request.retries < self.max_retries:
            print(f"[{time.strftime('%H:%M:%S')}] Ошибка: {exc}. Повторная попытка через 3 сек... "
                  f"({self.request.retries + 1}/{self.max_retries})")
        try:
            raise self.retry(exc=exc, countdown=3)
        except MaxRetriesExceededError as final_exc:
            raise final_exc

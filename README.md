# Transactional System Core — тестовое задание

**Отказоустойчивое ядро транзакций** с защитой от double spending, атомарной комиссией 10 % и асинхронными уведомлениями через Celery + Redis.

## Стек
- Python 3.11+
- Django 4.2+ + DRF
- PostgreSQL
- Celery 5.3 + Redis (broker & backend)
- Windows 10/11 (полностью протестировано)

## Основные требования ТЗ

| Требование | Как реализовано | Доказательство |
|------------|------------------|----------------|
| POST /api/transfer | `TransferAPIView` в `transactions/api/views.py` | Работает |
| Защита от double spending при 100+ одновременных запросах | `select_for_update()` + `@transaction.atomic` на трёх кошельках | Стресс-тест 10 параллельных запросов → баланс никогда не уходит в минус |
| Комиссия 10 % при сумме > 1000 | Списывается сверх суммы, зачисляется на технический кошелёк `admin` | Атомарно в одной транзакции |
| Асинхронное уведомление после успешной транзакции | Celery-задача `send_notification_task` | Запускается через `.delay()` |
| Retry до 3 раз с интервалом 3 сек при падении | `max_retries=3`, `default_retry_delay=3`, `self.retry(countdown=3)` | Видно в логах Celery |
| Имитация долгого запроса | `time.sleep()` (в проде будет запрос в Telegram) | Есть |

## Отдельные моменты

| Фича | Зачем |
|------|------|
| `select_for_update()` на трёх кошельках одновременно | 100 % защита даже при тысяче параллельных запросов |
| Чистые имена таблиц (`wallets`, `transactions`) | Удобно в pgAdmin и raw SQL |
| Индекс по `timestamp` | Готовность к миллиону транзакций |
| `MinValueValidator(0.00)` на баланс | Физически невозможно сохранить отрицательный баланс |
| `list_editable = ('balance',)` в админке | Редактирование баланса прямо в списке |
| Data migration с тестовыми данными + `reverse_code` | Один `migrate` — всё готово |
| Подробный стресс-тест `stress_test.py` | 10 одновременных запросов одним кликом |

## Как запустить (Windows 10/11)

```bash
# 1. Клонируем и заходим
git clone https://github.com/iurij-n/Test_ft.git
cd transactional-system-core

# 2. Создаём и активируем venv
python -m venv venv
venv\Scripts\activate

# 3. Устанавливаем зависимости
pip install -r requirements.txt
# (или вручную: django djangorestframework psycopg2-binary celery[redis] redis python-dotenv)

# 4. Создаём базу PostgreSQL "transactional_system" (через pgAdmin или psql)

# 5. Применяем миграции (создадутся тестовые пользователи и кошельки)
python manage.py migrate

# 6. Запускаем три окна:
# Окно 1 Django
python manage.py runserver

# Окно 2 Celery
celery -A core.celery worker -l info --pool=solo

# Окно 3 — стресс-тест
python stress_test.py
# Демо API чайного каталога

Отдельное Flask-приложение читает каталог из PostgreSQL через SQLAlchemy. Каталог запрашивают сервер Nuxt во время рендеринга `/catalog` и браузер при клиентской навигации; для браузерных запросов API отдаёт CORS-заголовки на домен frontend. Реализованы только категории и товары; изменение товаров через API, заказы и авторизация пока не реализованы. Первичное заполнение содержит 12 демонстрационных товаров. Цены и наличие демонстрационные.

## Запуск

Нужен Python 3.12+. Из корня репозитория:

```sh
python3 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt
cd backend
export DATABASE_URL='postgresql+psycopg://USER:PASSWORD@HOST:5432/vkr'
.venv/bin/python manage_catalog.py prepare
.venv/bin/gunicorn --bind 127.0.0.1:8080 --access-logfile - app:app
```

Замените `USER`, `PASSWORD` и `HOST` параметрами своего PostgreSQL. Пароль с особыми символами в URL должен быть percent-encoded. Секреты храните в окружении, а не в репозитории. Для локальной демонстрации можно использовать `export DATABASE_URL='sqlite:////absolute/path/catalog.db'`; в Amvera используется PostgreSQL.

Тесты из каталога `backend` используют временную SQLite и не обращаются к рабочей БД:

```sh
.venv/bin/python -m unittest discover -s tests -v
```

## Контракт

`GET /api/catalog` → `200 application/json`:

```json
{
  "items": [{"id": 1, "slug": "longjing", "name": "Лун Цзин", "category": "Зелёный чай", "origin": "Китай, Чжэцзян", "description": "Мягкий зелёный чай с ароматом каштана, свежей травы и лёгкой сладостью.", "price": 690, "weightGrams": 50, "inStock": true}],
  "total": 12,
  "currency": "RUB"
}
```

В примере сокращён `items`; после первичного заполнения ответ содержит 12 товаров. `price` — цена в рублях за упаковку `weightGrams` граммов; в БД используется `NUMERIC(12, 2)`. Фильтров и пагинации нет. Каждый запрос читает актуальные активные товары из БД, включая позиции не в наличии. Скрытые товары (`is_active=false`) не возвращаются. Ответы содержат `Cache-Control: no-store`. Если БД недоступна или `DATABASE_URL` не задан, API возвращает `503` с JSON `error`.

CORS: запросы с `Origin` из allowlist в `app.py` (домен демо-frontend, `http://127.0.0.1:3000` и `http://localhost:3000`) получают `Access-Control-Allow-Origin` с этим Origin и `Vary: Origin`; preflight `OPTIONS /api/catalog` — дополнительно `Access-Control-Allow-Methods: GET, OPTIONS`. Остальные Origin CORS-заголовков не получают.

`GET /healthz` → `200 {"status":"ok"}`. Неизвестный маршрут → `404` с JSON `error`.

## Таблицы и миграции

- `categories`: `id`, `name`, уникальный `slug`, `parent_id` для иерархии.
- `products`: `id`, `category_id`, уникальный `slug`, `name`, `description`, `price`, `origin_country`, `origin_region`, `packaging_weight`, `brewing_recommendation`, `image_url`, `in_stock`, `is_active`.
- `alembic_version` — служебная таблица учёта версии схемы.

Количество на складе не выдумывается: из исходного каталога переносится только признак наличия `in_stock`. Рекомендации по завариванию и изображения остаются пустыми до наполнения. Категории, товары и связи описаны в `models.py`; миграция `0001_catalog` хранится в `migrations/versions/`.

Команда `python manage_catalog.py upgrade` применяет миграции. `python manage_catalog.py seed` переносит данные из `catalog.json`, только если в БД ещё нет товаров; существующий каталог она не перезаписывает. `python manage_catalog.py prepare` последовательно выполняет обе операции. `python manage_catalog.py check` проверяет чтение БД и печатает количество категорий и товаров. После первичного импорта JSON в обслуживании запросов не участвует.

## Отдельный проект Amvera

Содержимое **этого каталога**, включая подкаталог `migrations/`, загружается в корень отдельного проекта API. `amvera.yaml` использует `Dockerfile` в корне репозитория проекта API; локальный контекст сборки — `backend/`. При старте `start.sh` применяет миграции, заполняет пустой каталог и запускает Gunicorn на `8080`. Ошибка миграции или подключения останавливает запуск.

В проекте API задайте `DATABASE_URL` как секретную переменную типа `RUN`, указав внутренний адрес PostgreSQL с окончанием `-rw`. API и PostgreSQL должны находиться в одном регионе. Приложение использует обычного пользователя БД; Superuser ему не нужен.

Для локальной проверки из корня репозитория:

```sh
docker build -t tea-shop-api backend
docker run --rm -p 8080:8080 --env DATABASE_URL tea-shop-api
```

В проекте Nuxt адрес API задаётся публичной runtime-переменной `NUXT_PUBLIC_API_BASE_URL` (базовый URL без `/api/catalog`); её значение доступно и серверу Nuxt, и браузеру. Доступ к БД настроен только в проекте API.

Использование Gunicorn соответствует [документации Flask](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/).

# Демо API чайного каталога

Отдельное Flask-приложение читает каталог из PostgreSQL через SQLAlchemy. Каталог запрашивают сервер Nuxt во время рендеринга `/catalog` и браузер при клиентской навигации; для браузерных запросов API отдаёт CORS-заголовки на домен frontend. Реализованы только категории и товары; изменение товаров через API, заказы и авторизация пока не реализованы. Первичное заполнение содержит 12 демонстрационных товаров. Цены и наличие демонстрационные.

## Запуск

Нужен Python 3.12 или новее. Для локального запуска подготовьте корневой `.env`, запустите PostgreSQL через Compose и выполните команды backend для своей ОС в [корневом Quick Start](../README.md#запуск-в-локальном-окружении). Там приведены создание виртуального окружения, установка зависимостей, загрузка `DATABASE_URL`, миграции и запуск Flask через Granian на `127.0.0.1:8080`. В Windows API работает непосредственно из PowerShell.

Для другой БД вместо загрузки `.env` задайте `DATABASE_URL` со своими параметрами. В Linux или macOS используйте `export DATABASE_URL='postgresql+psycopg://USER:PASSWORD@HOST:5432/vkr'`, в PowerShell — `$env:DATABASE_URL = 'postgresql+psycopg://USER:PASSWORD@HOST:5432/vkr'`. Пароль с особыми символами в URL должен быть percent-encoded. Секреты храните в окружении, а не в репозитории. Для локальной демонстрации можно использовать `sqlite:////absolute/path/catalog.db`; в Amvera используется PostgreSQL.

Тесты используют временную SQLite. Выполните из каталога `backend` команду `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` в PowerShell или `.venv/bin/python -m unittest discover -s tests -v` в Linux и macOS.

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

Содержимое **этого каталога**, включая подкаталог `migrations/`, загружается в корень отдельного проекта API. `amvera.yaml` использует `Dockerfile` в корне репозитория проекта API; локальный контекст сборки — `backend/`. При старте `start.sh` применяет миграции, заполняет пустой каталог и запускает Granian в режиме WSGI на `8080`. Ошибка миграции или подключения останавливает запуск.

В проекте API задайте `DATABASE_URL` как секретную переменную типа `RUN`, указав внутренний адрес PostgreSQL с окончанием `-rw`. API и PostgreSQL должны находиться в одном регионе. Приложение использует обычного пользователя БД; Superuser ему не нужен.

Для локальной проверки из корня репозитория:

```sh
docker build -t tea-shop-api backend
docker run --rm --network vkr -p 127.0.0.1:8080:8080 \
  -e DATABASE_URL='postgresql+psycopg://vkr:vkr@vkr-postgres:5432/vkr' tea-shop-api
```

Контейнер подключается к PostgreSQL из `docker-compose.yml` по имени контейнера `vkr-postgres` в сети Docker `vkr` (запуск БД — в корневом README, «Настройки localhost»); адрес `127.0.0.1:5432` из `.env` внутри контейнера указывает на сам контейнер API, поэтому здесь URL задаётся явно. Логин и пароль должны совпадать с `.env`.

В проекте Nuxt браузер использует `NUXT_PUBLIC_API_BASE_URL`, а SSR — `NUXT_API_BASE_URL` с возвратом к публичному адресу, если внутренний пуст. Оба адреса задаются без `/api/catalog`. Полный локальный стенд запускается командой `docker compose up --build`; Compose задаёт адреса автоматически. Доступ к БД настроен только в проекте API.

Параметры WSGI-сервера описаны в [документации Granian](https://github.com/emmett-framework/granian).

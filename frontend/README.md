# Nuxt frontend

Nuxt 4 с серверным рендерингом. Для каждого запроса `/catalog` сервер Nuxt получает JSON каталога из Flask напрямую по адресу из `NUXT_API_BASE_URL` (если пуст — из `NUXT_PUBLIC_API_BASE_URL`); при клиентской навигации браузер использует `NUXT_PUBLIC_API_BASE_URL`, поэтому API отдаёт CORS-заголовки на домен frontend. Прокси-маршрут `/api/catalog` на сервере Nuxt не используется. `await useFetch` дожидается данных перед рендерингом: названия, описания, цены и наличие находятся в исходном HTML. При гидратации используются данные Nuxt payload. Prerender и серверный кеш каталога отключены; ответы содержат `Cache-Control: no-store`.

Схема: браузер → Nuxt (runtime SSR) → Flask `/api/catalog` → JSON → HTML; при клиентской навигации — браузер → Flask напрямую (CORS).

## Локальный запуск

Нужен Node.js 24 LTS (ограничение `engines` в `package.json`). Из корня репозитория:

```sh
npm ci --prefix frontend
# Сначала запустить Flask по инструкции backend/README.md, порт 8080.
npm run dev --prefix frontend
```

Открыть http://127.0.0.1:3000/catalog. По умолчанию сервер обращается к `http://127.0.0.1:8080`.

Для использования демо API в Amvera:

```sh
NUXT_PUBLIC_API_BASE_URL=https://tea-shop-api-demo-vfirsov.msk1.amvera.tech npm run dev --prefix frontend
```

`NUXT_PUBLIC_API_BASE_URL` — базовый URL Flask без `/api/catalog`; значение доступно браузеру и служит резервным адресом для SSR. `NUXT_API_BASE_URL` задаёт отдельный адрес только для SSR и остаётся в серверной конфигурации. Переменная применяется при запуске готовой сборки, пересборка для смены адреса не требуется. Для development также можно скопировать `.env.example` в `.env`. Готовый Node-сервер не читает `.env`: переменную нужно передавать через окружение процесса.

## Проверки и production

```sh
npm run build --prefix frontend
npm run test:ssr --prefix frontend
NUXT_PUBLIC_API_BASE_URL=https://tea-shop-api-demo-vfirsov.msk1.amvera.tech npm start --prefix frontend
```

Сборка включает проверку типов. SSR-тест запускает production-сервер с тестовым API, проверяет товары в HTML без выполнения JS, изменение данных между двумя запросами без пересборки, HTTP 503 при сбое API, HTTP 404 удалённого прокси-маршрута `/api/catalog` и HTTP 404 неизвестной страницы. Flask отдельно проверяется тестами в `backend/tests`.

## Docker и Amvera

Полный локальный стенд (БД, API, frontend) запускается из корня репозитория:

```sh
docker compose up --build
```

Откройте `http://localhost:3000`. Compose задаёт `NUXT_API_BASE_URL=http://api:8080` для SSR и `NUXT_PUBLIC_API_BASE_URL=http://localhost:8080` для браузера на том же компьютере. Ручная настройка IP не требуется. Внутренний адрес хранится вне публичной runtime-конфигурации. Одинаковый ключ `catalog` в `useFetch` позволяет гидратации использовать SSR payload при разных адресах API.

Для отдельного контейнера с демо API:

Из корня репозитория:

```sh
docker build -f frontend/Dockerfile -t tea-shop-frontend .
docker run --rm -p 3000:80 -e NUXT_PUBLIC_API_BASE_URL=https://tea-shop-api-demo-vfirsov.msk1.amvera.tech tea-shop-frontend
```

`frontend/Dockerfile` запускает `.output/server/index.mjs` под Node.js 24; Nginx больше не используется. Контейнер слушает порт `80` — по нему Amvera маршрутизирует домен проекта; право binding порта ниже 1024 пользователю `node` даёт `setcap cap_net_bind_service` в Dockerfile. Проверка состояния — `/healthz`. В корневом `amvera.yaml` `containerPort` и `servicePort` равны `80`. Вариант с портом `3000` и явным `servicePort: 3000` у этого проекта не заработал: при исправном контейнере маршрут домена чередовал 503 и таймауты; возврат на `80`, на котором домен работал до перехода на Nuxt, устранил проблему. Для обновления существующего проекта Amvera нужно применить этот конфиг и задать RUN-переменную `NUXT_PUBLIC_API_BASE_URL`.

Flask развёрнут отдельно: проект `tea-shop-api-demo`, регион `msk1`, HTTPS https://tea-shop-api-demo-vfirsov.msk1.amvera.tech/api/catalog. Для API используется содержимое `backend/` и его собственный `amvera.yaml` (порт `8080`).

Демо-стенд обновлён до этой версии через MCP Amvera, без коммитов в GitHub. Lock-файл в репозиторий проекта не передавался (ограничение загрузки через API): Dockerfile выполняет `npm install` с точными версиями из `package.json`; при доставке кода через Git применяется `npm ci` по `package-lock.json`.

Документация Nuxt: [useFetch](https://nuxt.com/docs/4.x/api/composables/use-fetch), [runtime config](https://nuxt.com/docs/4.x/guide/going-further/runtime-config), [Node deployment](https://nuxt.com/docs/4.x/getting-started/deployment).

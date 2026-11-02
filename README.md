# Invix Telegram Bot

Небольшой Telegram-магазин с возможностью добавления товаров и просмотра каталога.

**Стек:** Next.js (App Router), FastAPI, aiogram 3, PostgreSQL, MinIO, Docker Compose и Traefik.

## Запуск проекта

Для запуска потребуется Docker Desktop с поддержкой Linux-контейнеров.

**1. Настройте окружение**

Скопируйте `.env.example` в `.env` и заполните настройки: токен Telegram-бота, Telegram ID администратора, пароли и публичный HTTPS-адрес Mini App (`MINI_APP_URL`).

**2. Запустите проект**

Из корневой папки:

```bash
docker compose up -d --build --scale backend=2 --scale frontend=2 --scale bot=2
```

Docker автоматически соберёт приложения, запустит PostgreSQL и MinIO, а также выполнит миграции базы данных.

**3. Откройте каталог**

http://127.0.0.1:18081

**4. Подключите Telegram**

Для работы Telegram Webhook и Mini App нужен публичный HTTPS-адрес. Можно использовать Tuna или другой HTTPS-туннель, направленный на локальный порт `18081`.

После запуска туннеля укажите его адрес в `MINI_APP_URL` и зарегистрируйте Webhook:

```bash
docker compose run --rm --no-deps bot python register_webhook.py
```

В BotFather настройте кнопку меню бота на тот же HTTPS-адрес.

## Использование

- `/start` — бот предложит открыть каталог через Telegram Mini App.
- `/create_product` — команда администратора для создания товара.
- Для добавления товара отправьте **фотографию с названием в подписи** одним сообщением.
- Добавленные товары появятся в каталоге Next.js, доступном в браузере и Telegram.

## Остановка

```bash
docker compose down
```

Данные PostgreSQL и MinIO сохраняются в Docker volumes.
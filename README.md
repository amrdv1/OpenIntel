# OpenIntel - Enterprise OSINT Platform

OpenIntel — это профессиональная OSINT-платформа, которая собирает, нормализует, анализирует и визуализирует исключительно публично доступные данные из открытых источников.

## Структура проекта (Этап 1)

Проект разделен на две основные части:

### 1. Backend (`/backend`)
Бэкенд написан на Python (FastAPI) и имеет следующую модульную архитектуру:
- `api/` — Контроллеры и роутеры FastAPI
- `services/` — Бизнес-логика приложения
- `adapters/` — Плагины (адаптеры) для интеграции с внешними источниками
- `workers/` — Фоновые задачи (Celery)
- `database/` — Модели БД (SQLAlchemy) и миграции (Alembic)
- `auth/` — Аутентификация, JWT, управление ролями (RBAC)
- `search/` — Интеграция с Elasticsearch
- `graph/` — Интеграция с Neo4j
- `cache/` — Кэширование с помощью Redis
- `config/` — Настройки проекта и переменные окружения

Зависимости управляются через `requirements.txt`. Точка входа: `main.py`.

### 2. Frontend (`/frontend`)
Фронтенд написан на React с использованием фреймворка Next.js (App Router), TypeScript и TailwindCSS.
Основные директории, которые будут созданы внутри фронтенда:
- `dashboard/` — Главная панель управления
- `search/` — Интерфейс поисковых запросов
- `report/` — Страница детализированного отчета
- `graph/` — Визуализация графа связей (Cytoscape.js)
- `settings/` — Настройки пользователя и системы

## Developer Guide (Инструкция по запуску)

### Запуск через Docker (Рекомендуется)
На Этапе 2 была добавлена полноценная поддержка Docker. Теперь вы можете запустить всю платформу одной командой.

1. Убедитесь, что у вас установлен Docker и Docker Compose.
2. В корневой директории выполните:
   ```bash
   docker-compose up -d --build
   ```
3. Доступные сервисы:
   - **Frontend (Next.js)**: [http://localhost](http://localhost) (через Nginx) или [http://localhost:3000](http://localhost:3000)
   - **Backend API**: [http://localhost/api/](http://localhost/api/)
   - **Swagger Docs**: [http://localhost/docs](http://localhost/docs)
   - **RabbitMQ Management**: [http://localhost:15672](http://localhost:15672) (guest/guest)
   - **Neo4j Browser**: [http://localhost:7474](http://localhost:7474) (neo4j/neo4j_pass)
   - **Grafana**: [http://localhost:3001](http://localhost:3001)

### Запуск локально (Без Docker)
*Если вам необходимо запустить сервисы отдельно:*

### Запуск Frontend
1. Перейдите в папку фронтенда: `cd frontend`
2. Установите зависимости (если они еще не установлены): `npm install`
3. Запустите сервер для разработки: `npm run dev`
4. Приложение будет доступно по адресу [http://localhost:3000](http://localhost:3000)

## Следующие этапы
Следующим шагом (Этап 3) будет подключение PostgreSQL к FastAPI-бэкенду. Мы настроим SQLAlchemy, создадим базовые модели и добавим систему миграций Alembic.

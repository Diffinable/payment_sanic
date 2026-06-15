# Payment Service API

Асинхронный REST API для управления пользователями, счетами и платежами с интеграцией вебхуков от платежной системы.

## Стек технологий

- **Backend:** Python 3.12, Sanic 24.x (асинхронный фреймворк)
- **Database:** PostgreSQL 15, SQLAlchemy 2.0 (async mode)
- **Migrations:** Alembic
- **Authentication:** JWT (python-jose)
- **Password hashing:** bcrypt
- **Containerization:** Docker, Docker Compose
- **API Documentation:** OpenAPI/Swagger (sanic-ext)

### Вариант 1: Запуск через Docker Compose

1. Клонируйте репозиторий:
```bash
git clone https://github.com/YOUR_USERNAME/payment-service.git
cd payment-service
```
2. Скопируйте файл конфигурации:

```bash
cp .env.example .env
```
3. Запустите контейнеры:

```bash
docker compose up -d --build
```
4. Примените миграции (создадут таблицы и тестовых пользователей):

```bash
docker compose exec app alembic upgrade head
```
5. Откройте документацию API:

```bash
http://localhost:8000/docs
```

###  Вариант 2: Запуск без Docker
1. Установите PostgreSQL 15+ и создайте базу данных:

```bash
createdb payment_db
```
2. Создайте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```
3. Установите зависимости:

```bash
pip install -r requirements.txt
```
4. Скопируйте и отредактируйте .env:

```bash
cp .env.example .env
```
Измените DB_URL на localhost:5432

5. Примените миграции:

```bash
alembic upgrade head
```
6. Запустите сервер:

```bash
python -m sanic app.server:app --host=0.0.0.0 --port=8000 --dev
```

###  Тестовые учетные данные
После применения миграций автоматически создаются:
### Обычный пользователь
Email: user@test.com
Password: user123
Права: просмотр своего профиля, счетов и платежей
### Администратор
Email: admin@test.com
Password: admin123
Права: управление пользователями (CRUD), просмотр всех счетов
##  API Endpoints
### Аутентификация
POST /auth/login — получить JWT-токен
### Пользователь (требуется Bearer token)
GET /users/me — получить свой профиль
GET /users/me/accounts — список своих счетов
GET /users/me/payments — история платежей
### Администратор (требуется Bearer token + is_admin=true)
GET /admin/users — список всех пользователей со счетами
POST /admin/users — создать пользователя
PUT /admin/users/<id> — обновить пользователя
DELETE /admin/users/<id> — удалить пользователя
# Вебхуки (публичный, проверяет подпись)
POST /webhook/payment — обработка платежа от платежной системы

# Chat Bot — Telegram бот с базой данных фильмов

Бот для рекомендации фильмов с регистрацией по номеру телефона, балансом и каталогом.

## Требования

- Python 3.11+
- PostgreSQL 17
- Git

---

## Установка

### 1. Клонировать репозиторий

```bash
git clone <ссылка_на_репозиторий>
cd Chat Bot
```

### 2. Создать виртуальное окружение

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

---

## Настройка PostgreSQL

### 1. Установить PostgreSQL 17

Скачать: https://www.postgresql.org/download/

При установке запомнить пароль пользователя `postgres`.

### 2. Создать базу данных и пользователя

Открыть psql:

```bash
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres
```

Выполнить:

```sql
CREATE DATABASE my_bot_db;
CREATE USER bot_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE my_bot_db TO bot_user;
ALTER DATABASE my_bot_db OWNER TO bot_user;
\c my_bot_db
GRANT ALL ON SCHEMA public TO bot_user;
\q
```

### 3. Восстановить данные из дампа

```bash
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U bot_user -d my_bot_db -f dump.sql
```

Если попросит пароль — ввести `secure_password`.

---

## Настройка config.py

Создать файл `config.py` в корне проекта:

```python
BOT_TOKEN = "токен_от_BotFather"
DATABASE_URL = "postgresql://bot_user:secure_password@localhost:5432/my_bot_db"
ADMIN_IDS = [твой_telegram_id]
```

**Где взять:**
- **BOT_TOKEN** — у @BotFather в Telegram (`/newbot`)
- **ADMIN_IDS** — у @userinfobot в Telegram

---

## Запуск

```bash
python main.py
```

Если всё настроено — бот запустится и будет отвечать в Telegram.

---

## Структура проекта

```
Chat Bot/
├── main.py           # Логика бота, обработчики
├── database.py       # Работа с PostgreSQL
├── config.py         # Секретные настройки (не в Git)
├── dump.sql          # Дамп базы данных
├── requirements.txt  # Зависимости
└── README.md
```

---


## Возможные проблемы

### Ошибка: `нет доступа к схеме public`

```sql
\c my_bot_db
GRANT ALL ON SCHEMA public TO bot_user;
```

### Ошибка: `psql не является командой`

Использовать полный путь:
```bash
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres
```

### Ошибка: `database "my_bot_db" does not exist`

Создать базу заново (шаг 2 раздела "Настройка PostgreSQL").

---

## Контакты

Автор: Kostyan4ike
Telegram: @chel22807

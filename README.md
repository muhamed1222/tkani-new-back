# MyShop Backend

Backend API для интернет-магазина тканей. REST API построен на Flask с использованием SQLAlchemy, JWT аутентификации и поддержкой загрузки файлов.

## 📋 Содержание

- [Технологии](#технологии)
- [Установка и настройка](#установка-и-настройка)
- [Структура проекта](#структура-проекта)
- [Конфигурация](#конфигурация)
- [Запуск проекта](#запуск-проекта)
- [API Endpoints](#api-endpoints)
- [База данных](#база-данных)
- [Аутентификация](#аутентификация)

## 🛠 Технологии

- **Python 3.8+**
- **Flask** - веб-фреймворк
- **SQLAlchemy** - ORM для работы с базой данных
- **Flask-JWT-Extended** - JWT аутентификация
- **Flask-CORS** - поддержка CORS для фронтенда
- **SQLite** - база данных (можно заменить на PostgreSQL/MySQL)

## 📦 Установка и настройка

### 1. Клонирование репозитория

```bash
git clone https://github.com/muhamed1222/tkani-new-back.git
cd tkani-new-back
```

### 2. Создание виртуального окружения

```bash
# Для macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Для Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения (опционально)

Проект работает с дефолтными настройками, но для production рекомендуется задать переменные окружения:

```bash
# macOS/Linux
export SECRET_KEY="your-secret-key-here"
export JWT_SECRET_KEY="your-jwt-secret-key-here"
export DATABASE_URL="sqlite:///app.db"

# Windows
set SECRET_KEY=your-secret-key-here
set JWT_SECRET_KEY=your-jwt-secret-key-here
set DATABASE_URL=sqlite:///app.db
```

## 📁 Структура проекта

```
myshop-backend/
├── app.py                 # Главный файл приложения
├── config.py              # Конфигурация приложения
├── models.py              # Модели базы данных (User, Product, Category, Order)
├── data_seed.py           # Скрипт для заполнения тестовыми данными
├── requirements.txt       # Зависимости проекта
├── .gitignore            # Игнорируемые файлы
├── routes/               # Маршруты API
│   ├── auth.py           # Аутентификация (регистрация, вход, профиль)
│   ├── catalog.py        # Каталог товаров и категории
│   ├── cart.py           # Корзина покупок (на основе cookies)
│   ├── orders.py         # Заказы
│   ├── admin.py          # Административные функции
│   └── utils.py          # Вспомогательные функции
└── static/               # Статические файлы
    └── avatars/          # Загруженные аватары пользователей
```

## ⚙️ Конфигурация

Основные настройки находятся в `config.py`:

- **SECRET_KEY** - секретный ключ Flask (по умолчанию: "dev-secret-key")
- **JWT_SECRET_KEY** - секретный ключ для JWT токенов (по умолчанию: "jwt-secret-string")
- **SQLALCHEMY_DATABASE_URI** - URI базы данных (по умолчанию: SQLite)
- **UPLOAD_FOLDER** - папка для загрузки файлов (`static/avatars`)
- **MAX_CONTENT_LENGTH** - максимальный размер загружаемого файла (2MB)
- **ALLOWED_EXTENSIONS** - разрешенные расширения для изображений (png, jpg, jpeg)

## 🚀 Запуск проекта

### Режим разработки

```bash
python app.py
```

Сервер запустится на `http://localhost:5000` в режиме отладки.

### Инициализация базы данных

База данных создается автоматически при первом запуске. Для заполнения тестовыми данными:

```bash
python data_seed.py
```

Это создаст:
- 2 категории (Electronics, Books)
- 3 товара
- Тестового пользователя (email: `test@example.com`, password: `password`)

## 🔌 API Endpoints

Все API endpoints имеют префикс `/api`

### 🔐 Аутентификация (`/api/auth`)

#### Регистрация пользователя
```http
POST /api/auth/register
Content-Type: multipart/form-data

Body:
  - first_name: string (required)
  - last_name: string (required)
  - email: string (required)
  - password: string (required)
  - avatar: file (optional, png/jpg/jpeg, max 2MB)
```

#### Вход в систему
```http
POST /api/auth/login
Content-Type: application/json

Body:
{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "user@example.com",
    "avatar": "static/avatars/xxx.jpg",
    "role": "user"
  }
}
```

#### Получить информацию о текущем пользователе
```http
GET /api/auth/me
Headers:
  Authorization: Bearer <access_token>
```

#### Обновить профиль
```http
PUT /api/auth/update
Headers:
  Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Body:
  - first_name: string (optional)
  - last_name: string (optional)
  - email: string (optional)
  - avatar: file (optional)
```

#### Изменить пароль
```http
POST /api/auth/change-password
Headers:
  Authorization: Bearer <access_token>
Content-Type: application/json

Body:
{
  "old_password": "oldpass123",
  "new_password": "newpass456"
}
```

#### Получить аватар пользователя
```http
GET /api/auth/avatar/<filename>
```

### 📦 Каталог товаров (`/api/catalog`)

#### Получить список товаров
```http
GET /api/catalog/products?q=search&category=1&min_price=10&max_price=100&sort=price_asc&page=1&per_page=12

Query Parameters:
  - q: string (поиск по названию)
  - category: int (фильтр по категории)
  - min_price: float (минимальная цена)
  - max_price: float (максимальная цена)
  - sort: string (price_asc, price_desc, title_asc, title_desc, id_desc)
  - page: int (номер страницы, по умолчанию: 1)
  - per_page: int (товаров на странице, по умолчанию: 12)

Response:
{
  "items": [...],
  "total": 50,
  "page": 1,
  "pages": 5
}
```

#### Получить список категорий
```http
GET /api/catalog/categories

Response:
[
  {"id": 1, "name": "Electronics"},
  {"id": 2, "name": "Books"}
]
```

#### Получить детали товара
```http
GET /api/catalog/products/<product_id>
```

### 🛒 Корзина (`/api/cart`)

Корзина работает на основе cookies. Все операции автоматически обновляют cookie `cart`.

#### Получить содержимое корзины
```http
GET /api/cart/

Response:
{
  "items": [
    {
      "product_id": 1,
      "title": "Smartphone",
      "price": 299.99,
      "quantity": 2,
      "line_total": 599.98
    }
  ],
  "subtotal": 599.98,
  "total": 599.98,
  "count": 2
}
```

#### Добавить товар в корзину
```http
POST /api/cart/add
Content-Type: application/json

Body:
{
  "product_id": 1,
  "quantity": 2
}
```

#### Удалить товар из корзины
```http
POST /api/cart/remove
Content-Type: application/json

Body:
{
  "product_id": 1
}
```

#### Обновить количество товара в корзине
```http
POST /api/cart/update
Content-Type: application/json

Body:
{
  "product_id": 1,
  "quantity": 3
}
```

### 📋 Заказы (`/api/orders`)

Все endpoints требуют аутентификации.

#### Создать заказ из корзины
```http
POST /api/orders/create
Headers:
  Authorization: Bearer <access_token>
```

Создает заказ на основе содержимого корзины (из cookie) и очищает корзину.

#### Получить список заказов пользователя
```http
GET /api/orders/my
Headers:
  Authorization: Bearer <access_token>

Response:
[
  {
    "id": 1,
    "created_at": "2024-01-15T10:30:00",
    "total": 599.98,
    "status": "created",
    "items": [
      {
        "product_id": 1,
        "title": "Smartphone",
        "quantity": 2,
        "price": 299.99
      }
    ]
  }
]
```

### 👨‍💼 Административные функции (`/api/admin`)

Все endpoints требуют аутентификации и роли `admin`.

#### Получить список всех товаров
```http
GET /api/admin/products
Headers:
  Authorization: Bearer <access_token>
```

#### Создать новый товар
```http
POST /api/admin/products
Headers:
  Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Body:
  - title: string (required)
  - description: string (optional)
  - price: float (required)
  - stock: int (optional, default: 0)
  - category_id: int (optional)
  - image: file (optional)
```

#### Обновить товар
```http
PUT /api/admin/products/<product_id>
Headers:
  Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Body: (все поля опциональны)
  - title: string
  - description: string
  - price: float
  - stock: int
  - category_id: int
  - image: file
```

#### Удалить товар
```http
DELETE /api/admin/products/<product_id>
Headers:
  Authorization: Bearer <access_token>
```

## 💾 База данных

### Модели

#### User (Пользователь)
- `id` - первичный ключ
- `first_name` - имя
- `last_name` - фамилия
- `email` - email (уникальный)
- `password_hash` - хеш пароля
- `avatar` - путь к аватару
- `role` - роль (user/admin)
- `created_at` - дата создания

#### Category (Категория)
- `id` - первичный ключ
- `name` - название категории (уникальное)

#### Product (Товар)
- `id` - первичный ключ
- `title` - название
- `description` - описание
- `price` - цена
- `stock` - количество на складе
- `image` - путь к изображению
- `category_id` - внешний ключ категории

#### Order (Заказ)
- `id` - первичный ключ
- `user_id` - внешний ключ пользователя
- `created_at` - дата создания
- `total` - общая сумма
- `status` - статус (created, paid, shipped, cancelled)

#### OrderItem (Позиция заказа)
- `id` - первичный ключ
- `order_id` - внешний ключ заказа
- `product_id` - внешний ключ товара
- `quantity` - количество
- `price` - цена на момент заказа

## 🔒 Аутентификация

Проект использует JWT (JSON Web Tokens) для аутентификации.

### Как использовать JWT токены

1. **Вход**: Отправьте POST запрос на `/api/auth/login` с email и password
2. **Получение токена**: В ответе получите `access_token`
3. **Использование**: Добавьте заголовок `Authorization: Bearer <access_token>` к защищенным запросам
4. **Истечение**: Токены не имеют срока истечения в текущей конфигурации (для production рекомендуется добавить срок)

### Права доступа

- **Публичные endpoints**: 
  - `/api/catalog/*`
  - `/api/cart/*`
  - `/api/auth/register`
  - `/api/auth/login`

- **Требуют аутентификации** (`@jwt_required`):
  - `/api/auth/me`
  - `/api/auth/update`
  - `/api/auth/change-password`
  - `/api/orders/*`

- **Требуют роль admin** (`@admin_required`):
  - `/api/admin/*`

## 📝 Примеры использования

### Регистрация пользователя

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -F "first_name=John" \
  -F "last_name=Doe" \
  -F "email=john@example.com" \
  -F "password=secret123"
```

### Вход в систему

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

### Получение списка товаров

```bash
curl http://localhost:5000/api/catalog/products?page=1&per_page=10
```

### Добавление товара в корзину

```bash
curl -X POST http://localhost:5000/api/cart/add \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":2}' \
  -c cookies.txt
```

### Создание заказа

```bash
curl -X POST http://localhost:5000/api/orders/create \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -b cookies.txt
```

## 🐛 Устранение неполадок

### Проблема: База данных не создается

**Решение**: Убедитесь, что у вас есть права на запись в директории проекта. База данных создается автоматически при первом запуске.

### Проблема: Ошибки CORS

**Решение**: Убедитесь, что Flask-CORS установлен и настроен. В текущей конфигурации CORS разрешен для всех источников с поддержкой credentials.

### Проблема: Файлы не загружаются

**Решение**: Проверьте, что папка `static/avatars` существует и имеет права на запись. Она создается автоматически при запуске.

## 📄 Лицензия

Этот проект создан для личного использования.

## 👤 Автор

**Muhamed**

- GitHub: [@muhamed1222](https://github.com/muhamed1222)

## 🔄 Версионирование

- **v1.0.0** - Первый релиз с базовым функционалом:
  - Аутентификация и авторизация
  - Каталог товаров
  - Корзина покупок
  - Заказы
  - Административная панель


# Инструкция по тестированию API работ

## Быстрый старт

### 1. Запустите Flask сервер

```bash
python app.py
```

Сервер должен запуститься на `http://localhost:5001` (порт 5001 используется, так как 5000 может быть занят AirPlay на macOS)

### 2. Добавьте тестовые данные

```bash
python seed_works.py
```

Это добавит 15 тестовых работ в базу данных.

### 3. Протестируйте API

#### Вариант A: Используя curl

```bash
curl 'http://localhost:5001/api/works?page=1&limit=12'
```

#### Вариант B: Используя тестовый скрипт

```bash
# Установите requests, если еще не установлен
pip install requests

# Запустите тесты
python test_api.py
```

#### Вариант C: В браузере

Откройте в браузере:
```
http://localhost:5001/api/works?page=1&limit=12
```

## Ожидаемый результат

При успешном запросе вы должны получить JSON ответ:

```json
{
  "works": [
    {
      "id": 1,
      "title": "Платье из вискозного шифона \"Флаурэль\" для выстаки \"Гранд Текстиль\"",
      "image": "/uploads/works/work1.jpg",
      "link": "/work/1"
    },
    ...
  ],
  "total": 15,
  "page": 1,
  "totalPages": 2
}
```

## Тестирование пагинации

```bash
# Первая страница (первые 12 работ)
curl 'http://localhost:5001/api/works?page=1&limit=12'

# Вторая страница (оставшиеся работы)
curl 'http://localhost:5001/api/works?page=2&limit=12'
```

## Проверка на фронтенде

1. Убедитесь, что фронтенд запущен:
   ```bash
   npm run dev
   ```

2. Откройте страницу работ: `http://localhost:5173/our_works`

3. Откройте DevTools (F12) и проверьте:
   - Вкладка **Network**: должен быть запрос к `/api/works` со статусом 200
   - Вкладка **Console**: не должно быть ошибок CORS

## Возможные проблемы

### CORS ошибка

Если видите ошибку CORS в консоли браузера, убедитесь, что в `app.py` настроен CORS:

```python
CORS(app, supports_credentials=True)
```

### 404 Not Found

Проверьте, что Blueprint зарегистрирован в `app.py`:
```python
from routes.works import works_bp
app.register_blueprint(works_bp, url_prefix="/api")
```

### Пустая база данных

Запустите скрипт для добавления тестовых данных:
```bash
python seed_works.py
```

## Автоматическое тестирование

Запустите полный набор тестов:

```bash
python test_api.py
```

Скрипт проверит:
- ✅ Базовый запрос к API
- ✅ Структуру ответа
- ✅ Пагинацию
- ✅ Валидацию параметров
- ✅ Формат данных работ


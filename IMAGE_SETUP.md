# Настройка изображений для работ

## Текущая ситуация

Изображения работ не загружаются, потому что:
1. В базе данных пути к изображениям: `/uploads/works/work1.jpg`
2. Файлы изображений отсутствуют в папке `static/works/`

## Решения

### Вариант 1: Добавить реальные изображения (рекомендуется)

1. Поместите изображения в папку:
   ```
   myshop-backend/static/works/
   ```

2. Назовите файлы:
   - `work1.jpg`
   - `work2.jpg`
   - `work3.jpg`
   - и т.д. (до `work15.jpg`)

3. API автоматически будет обслуживать их через endpoint `/api/works/image/<filename>`

### Вариант 2: Использовать placeholder изображения

Компонент `WorkCard` уже настроен на использование placeholder изображений, если основное не загружается.

### Вариант 3: Создать placeholder изображения программно

Если установлен Pillow:

```bash
pip install Pillow
python3 create_placeholder_images.py
```

Это создаст простые placeholder изображения в папке `static/works/`.

## Проверка

После добавления изображений:

1. Перезапустите бэкенд сервер
2. Обновите страницу фронтенда
3. Изображения должны загрузиться

## Endpoint для изображений

API автоматически обслуживает изображения через:
```
GET http://localhost:5001/api/works/image/<filename>
```

Например:
```
GET http://localhost:5001/api/works/image/work1.jpg
```

## Формат URL в API

API автоматически преобразует пути из базы данных в полные URL:
- Из: `/uploads/works/work1.jpg`
- В: `http://localhost:5001/api/works/image/work1.jpg`


"""
Скрипт для работы с миграциями базы данных
Использование:
    flask db init          - инициализация миграций
    flask db migrate       - создание миграции
    flask db upgrade       - применение миграций
    flask db downgrade     - откат миграции
"""
from app import create_app
from flask_migrate import Migrate
from models import db

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()


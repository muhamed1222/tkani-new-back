"""
Конфигурация для pytest
"""
import pytest
import os
import tempfile
from app import create_app
from models import db

@pytest.fixture
def app():
    """Создает тестовое приложение"""
    # Создаем временную БД
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 300  # 5 минут для тестов
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Тестовый клиент"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Тестовый CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client):
    """Получить заголовки авторизации для тестов"""
    # Регистрируем тестового пользователя
    response = client.post('/api/v1/auth/register', 
        data={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'testpass123'
        })
    
    # Входим
    response = client.post('/api/v1/auth/login',
        json={
            'email': 'test@example.com',
            'password': 'testpass123'
        })
    
    data = response.get_json()
    token = data.get('access_token')
    
    return {
        'Authorization': f'Bearer {token}'
    }

@pytest.fixture
def admin_headers(client, app):
    """Получить заголовки авторизации для админа"""
    from models import User
    
    with app.app_context():
        # Создаем админа
        admin = User(
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('adminpass123')
        db.session.add(admin)
        db.session.commit()
    
    # Входим как админ
    response = client.post('/api/v1/auth/login',
        json={
            'email': 'admin@example.com',
            'password': 'adminpass123'
        })
    
    data = response.get_json()
    token = data.get('access_token')
    
    return {
        'Authorization': f'Bearer {token}'
    }


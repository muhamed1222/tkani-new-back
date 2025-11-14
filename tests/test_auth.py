"""
Тесты для аутентификации
"""
import pytest
from models import User, db

def test_register(client):
    """Тест регистрации пользователя"""
    response = client.post('/api/v1/auth/register', 
        data={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'password123'
        })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] == True
    assert 'user' in data
    assert data['user']['email'] == 'john@example.com'

def test_register_duplicate_email(client):
    """Тест регистрации с существующим email"""
    # Первая регистрация
    client.post('/api/v1/auth/register', 
        data={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'password123'
        })
    
    # Вторая регистрация с тем же email
    response = client.post('/api/v1/auth/register', 
        data={
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'password456'
        })
    
    assert response.status_code == 409

def test_login(client):
    """Тест входа в систему"""
    # Регистрируем пользователя
    client.post('/api/v1/auth/register', 
        data={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'password123'
        })
    
    # Входим
    response = client.post('/api/v1/auth/login',
        json={
            'email': 'john@example.com',
            'password': 'password123'
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'access_token' in data
    assert 'user' in data

def test_login_wrong_password(client):
    """Тест входа с неверным паролем"""
    # Регистрируем пользователя
    client.post('/api/v1/auth/register', 
        data={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'password123'
        })
    
    # Пытаемся войти с неверным паролем
    response = client.post('/api/v1/auth/login',
        json={
            'email': 'john@example.com',
            'password': 'wrongpassword'
        })
    
    assert response.status_code == 401

def test_get_me(auth_headers, client):
    """Тест получения информации о текущем пользователе"""
    response = client.get('/api/v1/auth/me', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'user' in data
    assert data['user']['email'] == 'test@example.com'

def test_get_me_unauthorized(client):
    """Тест получения информации без авторизации"""
    response = client.get('/api/v1/auth/me')
    
    assert response.status_code == 401

def test_change_password(auth_headers, client):
    """Тест смены пароля"""
    response = client.post('/api/v1/auth/change-password',
        headers=auth_headers,
        json={
            'old_password': 'testpass123',
            'new_password': 'newpass123'
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    
    # Проверяем, что новый пароль работает
    response = client.post('/api/v1/auth/login',
        json={
            'email': 'test@example.com',
            'password': 'newpass123'
        })
    assert response.status_code == 200

def test_update_profile(auth_headers, client):
    """Тест обновления профиля"""
    response = client.put('/api/v1/auth/update',
        headers=auth_headers,
        data={
            'first_name': 'Updated',
            'last_name': 'Name'
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert data['user']['first_name'] == 'Updated'
    assert data['user']['last_name'] == 'Name'

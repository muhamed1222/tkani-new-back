"""
Тесты для административных функций
"""
import pytest
from models import Product, Category, db

def test_list_all_products(admin_headers, client):
    """Тест получения списка всех товаров (админ)"""
    response = client.get('/api/v1/admin/products',
        headers=admin_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'products' in data

def test_create_product(admin_headers, client):
    """Тест создания товара"""
    response = client.post('/api/v1/admin/products',
        headers=admin_headers,
        data={
            'title': 'New Product',
            'description': 'Test description',
            'price': 25.0,
            'stock': 5
        })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] == True
    assert data['product']['title'] == 'New Product'
    assert data['product']['price'] == 25.0

def test_update_product(admin_headers, client):
    """Тест обновления товара"""
    # Создаем товар
    create_response = client.post('/api/v1/admin/products',
        headers=admin_headers,
        data={
            'title': 'Product to Update',
            'price': 10.0,
            'stock': 5
        })
    product_id = create_response.get_json()['product']['id']
    
    # Обновляем товар
    response = client.put(f'/api/v1/admin/products/{product_id}',
        headers=admin_headers,
        data={
            'title': 'Updated Product',
            'price': 15.0
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert data['product']['title'] == 'Updated Product'
    assert data['product']['price'] == 15.0

def test_delete_product(admin_headers, client):
    """Тест удаления товара"""
    # Создаем товар
    create_response = client.post('/api/v1/admin/products',
        headers=admin_headers,
        data={
            'title': 'Product to Delete',
            'price': 10.0,
            'stock': 5
        })
    product_id = create_response.get_json()['product']['id']
    
    # Удаляем товар
    response = client.delete(f'/api/v1/admin/products/{product_id}',
        headers=admin_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    
    # Проверяем, что товар удален
    get_response = client.get(f'/api/v1/catalog/products/{product_id}')
    assert get_response.status_code == 404

def test_admin_access_required(client):
    """Тест что админские функции требуют прав администратора"""
    response = client.get('/api/v1/admin/products')
    
    assert response.status_code == 401

def test_regular_user_cannot_access_admin(auth_headers, client):
    """Тест что обычный пользователь не может получить доступ к админским функциям"""
    response = client.get('/api/v1/admin/products',
        headers=auth_headers)
    
    assert response.status_code == 403


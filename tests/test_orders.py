"""
Тесты для заказов
"""
import pytest
from models import Product, Order, db

@pytest.fixture
def sample_product_for_order(app):
    """Создать тестовый товар для заказа"""
    with app.app_context():
        product = Product(title="Order Product", price=15.0, stock=10)
        db.session.add(product)
        db.session.commit()
        return product.id

def test_create_order(auth_headers, client, sample_product_for_order):
    """Тест создания заказа"""
    # Добавляем товар в корзину
    client.post('/api/v1/cart/add',
        json={
            'product_id': sample_product_for_order,
            'quantity': 2
        })
    
    # Создаем заказ
    response = client.post('/api/v1/orders/create',
        headers=auth_headers)
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] == True
    assert 'order_id' in data

def test_create_order_empty_cart(auth_headers, client):
    """Тест создания заказа с пустой корзиной"""
    response = client.post('/api/v1/orders/create',
        headers=auth_headers)
    
    assert response.status_code == 400

def test_get_my_orders(auth_headers, client, sample_product_for_order):
    """Тест получения списка заказов"""
    # Создаем заказ
    client.post('/api/v1/cart/add',
        json={
            'product_id': sample_product_for_order,
            'quantity': 1
        })
    client.post('/api/v1/orders/create',
        headers=auth_headers)
    
    # Получаем список заказов
    response = client.get('/api/v1/orders/my',
        headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'orders' in data
    assert len(data['orders']) >= 1

def test_get_order_detail(auth_headers, client, sample_product_for_order):
    """Тест получения деталей заказа"""
    # Создаем заказ
    client.post('/api/v1/cart/add',
        json={
            'product_id': sample_product_for_order,
            'quantity': 1
        })
    create_response = client.post('/api/v1/orders/create',
        headers=auth_headers)
    order_id = create_response.get_json()['order_id']
    
    # Получаем детали заказа
    response = client.get(f'/api/v1/orders/{order_id}',
        headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'order' in data
    assert data['order']['id'] == order_id

def test_update_order_status(auth_headers, client, sample_product_for_order):
    """Тест обновления статуса заказа"""
    # Создаем заказ
    client.post('/api/v1/cart/add',
        json={
            'product_id': sample_product_for_order,
            'quantity': 1
        })
    create_response = client.post('/api/v1/orders/create',
        headers=auth_headers)
    order_id = create_response.get_json()['order_id']
    
    # Обновляем статус
    response = client.put(f'/api/v1/orders/{order_id}/status',
        headers=auth_headers,
        json={
            'status': 'paid',
            'comment': 'Payment received'
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert data['status'] == 'paid'


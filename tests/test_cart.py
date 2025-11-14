"""
Тесты для корзины
"""
import pytest
from models import Product, Category, db

@pytest.fixture
def sample_product(app):
    """Создать тестовый товар"""
    with app.app_context():
        product = Product(title="Test Product", price=10.0, stock=10)
        db.session.add(product)
        db.session.commit()
        product_id = product.id
        return product_id

def test_get_empty_cart(client):
    """Тест получения пустой корзины"""
    response = client.get('/api/v1/cart/')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert data['items'] == []
    assert data['total'] == 0
    assert data['count'] == 0

def test_add_to_cart(client, sample_product):
    """Тест добавления товара в корзину"""
    response = client.post('/api/v1/cart/add',
        json={
            'product_id': sample_product,
            'quantity': 2
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert len(data['items']) == 1
    assert data['items'][0]['product_id'] == sample_product
    assert data['items'][0]['quantity'] == 2
    assert data['total'] == 20.0

def test_update_cart(client, sample_product):
    """Тест обновления количества товара в корзине"""
    # Добавляем товар
    client.post('/api/v1/cart/add',
        json={
            'product_id': sample_product,
            'quantity': 2
        })
    
    # Обновляем количество
    response = client.post('/api/v1/cart/update',
        json={
            'product_id': sample_product,
            'quantity': 5
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['items'][0]['quantity'] == 5
    assert data['total'] == 50.0

def test_remove_from_cart(client, sample_product):
    """Тест удаления товара из корзины"""
    # Добавляем товар
    client.post('/api/v1/cart/add',
        json={
            'product_id': sample_product,
            'quantity': 2
        })
    
    # Удаляем товар
    response = client.post('/api/v1/cart/remove',
        json={
            'product_id': sample_product
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) == 0
    assert data['total'] == 0

def test_clear_cart(client, sample_product):
    """Тест очистки корзины"""
    # Добавляем товар
    client.post('/api/v1/cart/add',
        json={
            'product_id': sample_product,
            'quantity': 2
        })
    
    # Очищаем корзину
    response = client.post('/api/v1/cart/clear')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert len(data['items']) == 0
    assert data['total'] == 0

def test_add_nonexistent_product(client):
    """Тест добавления несуществующего товара"""
    response = client.post('/api/v1/cart/add',
        json={
            'product_id': 999,
            'quantity': 1
        })
    
    assert response.status_code == 404


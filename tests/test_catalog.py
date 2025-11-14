"""
Тесты для каталога
"""
import pytest
from models import Product, Category, db

@pytest.fixture
def sample_category(app):
    """Создать тестовую категорию"""
    with app.app_context():
        category = Category(name="Test Category")
        db.session.add(category)
        db.session.commit()
        db.session.refresh(category)  # Обновляем объект из БД
        category_id = category.id  # Сохраняем ID
        db.session.expunge(category)  # Отсоединяем от сессии
        return category_id

@pytest.fixture
def sample_products(app, sample_category):
    """Создать тестовые товары"""
    with app.app_context():
        products = [
            Product(title="Product 1", price=10.0, stock=5, category_id=sample_category),
            Product(title="Product 2", price=20.0, stock=10, category_id=sample_category),
            Product(title="Another Product", price=15.0, stock=3, category_id=None),
        ]
        for product in products:
            db.session.add(product)
        db.session.commit()
        # Сохраняем ID продуктов
        product_ids = [p.id for p in products]
        return product_ids

def test_list_products(client, sample_products):
    """Тест получения списка товаров"""
    response = client.get('/api/v1/catalog/products')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'items' in data
    assert len(data['items']) >= 3

def test_list_products_with_search(client, sample_products):
    """Тест поиска товаров"""
    response = client.get('/api/v1/catalog/products?q=Product')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert len(data['items']) >= 2  # Product 1 и Product 2

def test_list_products_with_category(client, sample_products, sample_category):
    """Тест фильтрации по категории"""
    response = client.get(f'/api/v1/catalog/products?category={sample_category}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert len(data['items']) >= 2

def test_list_products_with_price_filter(client, sample_products):
    """Тест фильтрации по цене"""
    response = client.get('/api/v1/catalog/products?min_price=12&max_price=18')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert len(data['items']) >= 1  # Another Product

def test_list_products_pagination(client, sample_products):
    """Тест пагинации"""
    response = client.get('/api/v1/catalog/products?page=1&per_page=2')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert len(data['items']) == 2
    assert data['page'] == 1

def test_get_product_detail(client, sample_products):
    """Тест получения деталей товара"""
    product_id = sample_products[0]
    response = client.get(f'/api/v1/catalog/products/{product_id}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'product' in data
    assert data['product']['id'] == product_id

def test_get_product_not_found(client):
    """Тест получения несуществующего товара"""
    response = client.get('/api/v1/catalog/products/999')
    
    assert response.status_code == 404

def test_list_categories(client, sample_category):
    """Тест получения списка категорий"""
    response = client.get('/api/v1/catalog/categories')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'categories' in data
    assert len(data['categories']) >= 1

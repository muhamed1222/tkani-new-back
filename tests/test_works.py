"""
Тесты для работ
"""
import pytest
from models import Work, db

@pytest.fixture
def sample_works(app):
    """Создать тестовые работы"""
    with app.app_context():
        works = [
            Work(title="Work 1", image="work1.jpg", link="/work/1"),
            Work(title="Work 2", image="work2.jpg", link="/work/2"),
            Work(title="Work 3", image="work3.jpg", link="/work/3"),
        ]
        for work in works:
            db.session.add(work)
        db.session.commit()
        return [w.id for w in works]

def test_get_works(client, sample_works):
    """Тест получения списка работ"""
    response = client.get('/api/v1/works?page=1&limit=10')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'works' in data
    assert len(data['works']) >= 3

def test_get_works_pagination(client, sample_works):
    """Тест пагинации работ"""
    response = client.get('/api/v1/works?page=1&limit=2')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert len(data['works']) == 2
    assert data['page'] == 1

def test_get_works_second_page(client, sample_works):
    """Тест получения второй страницы работ"""
    response = client.get('/api/v1/works?page=2&limit=2')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert data['page'] == 2


"""
Скрипт для добавления тестовых брендов
"""
from app import create_app
from models import db, Brand

app = create_app()

with app.app_context():
    brands_data = [
        {'name': 'Египет', 'slug': 'egypt'},
        {'name': 'Азия', 'slug': 'asia'},
        {'name': 'Турция', 'slug': 'turkey'},
        {'name': 'Россия', 'slug': 'russia'},
        {'name': 'Италия', 'slug': 'italy'},
    ]
    
    existing_count = Brand.query.count()
    print(f"Текущее количество брендов в базе: {existing_count}")
    
    added_count = 0
    for brand_data in brands_data:
        existing = Brand.query.filter_by(slug=brand_data['slug']).first()
        if not existing:
            brand = Brand(**brand_data)
            db.session.add(brand)
            added_count += 1
    
    db.session.commit()
    print(f"✅ Добавлено новых брендов: {added_count}")
    print(f"✅ Всего брендов в базе: {Brand.query.count()}")


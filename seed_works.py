"""
Скрипт для добавления тестовых данных работ в базу данных
"""
from app import create_app
from models import db, Work

app = create_app()

with app.app_context():
    # Создаем тестовые работы
    works_data = [
        {
            'title': 'Платье из вискозного шифона "Флаурэль" для выстаки "Гранд Текстиль"',
            'image': '/uploads/works/work1.jpg',
            'link': '/work/1'
        },
        {
            'title': 'Платье из вискозного шифона "Флаурэль" для выстаки "Гранд Текстиль"',
            'image': '/uploads/works/work2.jpg',
            'link': '/work/2'
        },
        {
            'title': 'Блузка из натурального шелка "Премиум Коллекция"',
            'image': '/uploads/works/work3.jpg',
            'link': '/work/3'
        },
        {
            'title': 'Юбка из льняной ткани "Эко Стиль"',
            'image': '/uploads/works/work4.jpg',
            'link': '/work/4'
        },
        {
            'title': 'Платье из хлопкового сатина "Летняя коллекция"',
            'image': '/uploads/works/work5.jpg',
            'link': '/work/5'
        },
        {
            'title': 'Жакет из шерстяной ткани "Классика"',
            'image': '/uploads/works/work6.jpg',
            'link': '/work/6'
        },
        {
            'title': 'Брюки из вискозного крепа "Офисный стиль"',
            'image': '/uploads/works/work7.jpg',
            'link': '/work/7'
        },
        {
            'title': 'Платье из атласа "Вечерний наряд"',
            'image': '/uploads/works/work8.jpg',
            'link': '/work/8'
        },
        {
            'title': 'Туника из батиста "Повседневная коллекция"',
            'image': '/uploads/works/work9.jpg',
            'link': '/work/9'
        },
        {
            'title': 'Платье из органзы "Свадебная коллекция"',
            'image': '/uploads/works/work10.jpg',
            'link': '/work/10'
        },
        {
            'title': 'Жилет из джинсовой ткани "Кэжуал стиль"',
            'image': '/uploads/works/work11.jpg',
            'link': '/work/11'
        },
        {
            'title': 'Платье из креп-сатина "Деловой стиль"',
            'image': '/uploads/works/work12.jpg',
            'link': '/work/12'
        },
        {
            'title': 'Блузка из шифона "Романтическая коллекция"',
            'image': '/uploads/works/work13.jpg',
            'link': '/work/13'
        },
        {
            'title': 'Юбка из твида "Осенняя коллекция"',
            'image': '/uploads/works/work14.jpg',
            'link': '/work/14'
        },
        {
            'title': 'Платье из бархата "Зимняя коллекция"',
            'image': '/uploads/works/work15.jpg',
            'link': '/work/15'
        }
    ]
    
    # Проверяем, есть ли уже работы в базе
    existing_count = Work.query.count()
    print(f"Текущее количество работ в базе: {existing_count}")
    
    # Добавляем работы
    added_count = 0
    for work_data in works_data:
        # Проверяем, не существует ли уже работа с таким же title и image
        existing = Work.query.filter_by(
            title=work_data['title'],
            image=work_data['image']
        ).first()
        
        if not existing:
            work = Work(**work_data)
            db.session.add(work)
            added_count += 1
    
    db.session.commit()
    print(f"✅ Добавлено новых работ: {added_count}")
    print(f"✅ Всего работ в базе: {Work.query.count()}")


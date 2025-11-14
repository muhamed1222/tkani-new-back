#!/usr/bin/env python3
"""
Скрипт для создания администратора
"""
from app import create_app
from models import db, User

def create_admin():
    app = create_app()
    
    with app.app_context():
        # Проверяем, есть ли уже администратор
        existing_admin = User.query.filter_by(role='admin').first()
        if existing_admin:
            print(f"⚠️  Администратор уже существует: {existing_admin.email}")
            response = input("Создать еще одного? (y/n): ")
            if response.lower() != 'y':
                print("Отменено.")
                return
        
        # Запрашиваем данные
        print("\n=== Создание администратора ===")
        first_name = input("Имя: ").strip() or "Admin"
        last_name = input("Фамилия: ").strip() or "User"
        email = input("Email: ").strip()
        
        if not email:
            print("❌ Email обязателен!")
            return
        
        # Проверяем, существует ли пользователь с таким email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"⚠️  Пользователь с email {email} уже существует!")
            response = input("Изменить роль на admin? (y/n): ")
            if response.lower() == 'y':
                existing_user.role = 'admin'
                db.session.commit()
                print(f"✅ Роль пользователя {email} изменена на admin")
            return
        
        password = input("Пароль: ").strip()
        if not password:
            print("❌ Пароль обязателен!")
            return
        
        # Создаем администратора
        admin = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            role='admin'
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"\n✅ Администратор успешно создан!")
        print(f"   Email: {email}")
        print(f"   Имя: {first_name} {last_name}")
        print(f"\nТеперь вы можете войти в админ-панель по адресу:")
        print(f"   http://localhost:5173/admin")

if __name__ == '__main__':
    create_admin()


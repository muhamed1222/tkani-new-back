import os
from flask import current_app
from werkzeug.utils import secure_filename
from uuid import uuid4

def allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']

def save_avatar(file_storage):
    """Сохранить аватар пользователя"""
    if not allowed_file(file_storage.filename):
        return None
    filename = secure_filename(file_storage.filename)
    unique = f"{uuid4().hex}_{filename}"
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique)
    file_storage.save(path)
    return os.path.join("static", "avatars", unique)

def save_product_image(file_storage):
    """Сохранить изображение товара"""
    if not allowed_file(file_storage.filename):
        return None
    filename = secure_filename(file_storage.filename)
    unique = f"{uuid4().hex}_{filename}"
    upload_folder = current_app.config.get('PRODUCTS_UPLOAD_FOLDER')
    if not upload_folder:
        upload_folder = os.path.join(
            os.path.dirname(current_app.config['UPLOAD_FOLDER']),
            "products"
        )
    os.makedirs(upload_folder, exist_ok=True)
    path = os.path.join(upload_folder, unique)
    file_storage.save(path)
    return os.path.join("static", "products", unique)

def save_work_image(file_storage):
    """Сохранить изображение работы"""
    if not allowed_file(file_storage.filename):
        return None
    filename = secure_filename(file_storage.filename)
    unique = f"{uuid4().hex}_{filename}"
    upload_folder = current_app.config.get('WORKS_UPLOAD_FOLDER')
    if not upload_folder:
        upload_folder = os.path.join(
            os.path.dirname(current_app.config['UPLOAD_FOLDER']),
            "works"
        )
    os.makedirs(upload_folder, exist_ok=True)
    path = os.path.join(upload_folder, unique)
    file_storage.save(path)
    return os.path.join("static", "works", unique)
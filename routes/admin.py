from flask import Blueprint, request, jsonify, current_app
from models import db, Product, Category, User
from routes.utils import save_avatar, allowed_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import os

admin_bp = Blueprint("admin", __name__)

def admin_required(f):
    """Декоратор для проверки прав администратора"""
    from functools import wraps
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != "admin":
            return jsonify({"msg": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/products", methods=["GET"])
@admin_required
def list_all_products():
    """Получить список всех товаров (для админа)"""
    products = Product.query.all()
    return jsonify([{
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "price": p.price,
        "stock": p.stock,
        "image": p.image,
        "category_id": p.category_id
    } for p in products]), 200

@admin_bp.route("/products", methods=["POST"])
@admin_required
def create_product():
    """Создать новый товар"""
    data = request.form.to_dict()
    
    if not data.get("title") or not data.get("price"):
        return jsonify({"msg": "Missing title or price"}), 400
    
    product = Product(
        title=data["title"],
        description=data.get("description", ""),
        price=float(data["price"]),
        stock=int(data.get("stock", 0)),
        category_id=int(data["category_id"]) if data.get("category_id") else None
    )
    
    # Обработка изображения
    if "image" in request.files:
        f = request.files["image"]
        if f.filename:
            # Сохраняем в папку static/products
            upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'].replace('avatars', 'products'))
            os.makedirs(upload_folder, exist_ok=True)
            
            from werkzeug.utils import secure_filename
            from uuid import uuid4
            filename = secure_filename(f.filename)
            unique = f"{uuid4().hex}_{filename}"
            path = os.path.join(upload_folder, unique)
            f.save(path)
            product.image = os.path.join("static", "products", unique)
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        "id": product.id,
        "title": product.title,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "image": product.image,
        "category_id": product.category_id
    }), 201

@admin_bp.route("/products/<int:product_id>", methods=["PUT"])
@admin_required
def update_product(product_id):
    """Обновить товар"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"msg": "Product not found"}), 404
    
    data = request.form.to_dict()
    
    if "title" in data:
        product.title = data["title"]
    if "description" in data:
        product.description = data["description"]
    if "price" in data:
        product.price = float(data["price"])
    if "stock" in data:
        product.stock = int(data["stock"])
    if "category_id" in data:
        product.category_id = int(data["category_id"]) if data["category_id"] else None
    
    # Обновление изображения
    if "image" in request.files:
        f = request.files["image"]
        if f.filename:
            upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'].replace('avatars', 'products'))
            os.makedirs(upload_folder, exist_ok=True)
            
            from werkzeug.utils import secure_filename
            from uuid import uuid4
            filename = secure_filename(f.filename)
            unique = f"{uuid4().hex}_{filename}"
            path = os.path.join(upload_folder, unique)
            f.save(path)
            product.image = os.path.join("static", "products", unique)
    
    db.session.commit()
    
    return jsonify({
        "id": product.id,
        "title": product.title,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "image": product.image,
        "category_id": product.category_id
    }), 200

@admin_bp.route("/products/<int:product_id>", methods=["DELETE"])
@admin_required
def delete_product(product_id):
    """Удалить товар"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"msg": "Product not found"}), 404
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({"msg": "Product deleted"}), 200


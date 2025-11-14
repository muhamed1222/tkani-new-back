from flask import Blueprint, request, jsonify, current_app
from models import db, Product, Category, User, Order, OrderItem, OrderHistory
from routes.utils import save_product_image
from flask_jwt_extended import jwt_required, get_jwt_identity
from errors import NotFoundError, ValidationError, ForbiddenError
from schemas import ProductCreateSchema, ProductUpdateSchema, ProductSchema, OrderSchema
from marshmallow import ValidationError as MarshmallowValidationError
from sqlalchemy import func
from sqlalchemy.orm import joinedload
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
            raise ForbiddenError("Требуются права администратора")
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/products", methods=["GET"])
@admin_required
def list_all_products():
    """
    Получить список всех товаров (для админа)
    ---
    tags:
      - admin
    security:
      - Bearer: []
    responses:
      200:
        description: Список всех товаров
    """
    try:
        products = Product.query.order_by(Product.id.desc()).all()
        product_schema = ProductSchema(many=True)
        
        return jsonify({
            "success": True,
            "products": product_schema.dump(products)
        }), 200
    except Exception as e:
        raise ValidationError(f"Ошибка при получении товаров: {str(e)}")

@admin_bp.route("/products", methods=["POST"])
@admin_required
def create_product():
    """
    Создать новый товар
    ---
    tags:
      - admin
    security:
      - Bearer: []
    parameters:
      - name: title
        in: formData
        type: string
        required: true
      - name: description
        in: formData
        type: string
      - name: price
        in: formData
        type: number
        required: true
      - name: stock
        in: formData
        type: integer
      - name: category_id
        in: formData
        type: integer
      - name: image
        in: formData
        type: file
    responses:
      201:
        description: Товар создан
    """
    try:
        schema = ProductCreateSchema()
        try:
            data = schema.load(request.form.to_dict())
        except MarshmallowValidationError as err:
            raise ValidationError(f"Ошибка валидации: {err.messages}")
        
        product = Product(
            title=data["title"],
            description=data.get("description", ""),
            price=data["price"],
            stock=data.get("stock", 0),
            category_id=data.get("category_id"),
            brand_id=data.get("brand_id")
        )
        
        # Обработка изображения
        if "image" in request.files:
            f = request.files["image"]
            if f.filename:
                saved = save_product_image(f)
                if saved is None:
                    raise ValidationError("Недопустимое расширение файла изображения")
                product.image = saved
        
        db.session.add(product)
        db.session.commit()
        
        # Очищаем кэш каталога
        cache = current_app.cache
        cache.delete_memoized(list_all_products)
        cache.delete("categories_list")
        
        product_schema = ProductSchema()
        return jsonify({
            "success": True,
            "message": "Товар успешно создан",
            "product": product_schema.dump(product)
        }), 201
    except ValidationError as e:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Ошибка при создании товара: {str(e)}")

@admin_bp.route("/products/<int:product_id>", methods=["PUT"])
@admin_required
def update_product(product_id):
    """
    Обновить товар
    ---
    tags:
      - admin
    security:
      - Bearer: []
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
      - name: title
        in: formData
        type: string
      - name: description
        in: formData
        type: string
      - name: price
        in: formData
        type: number
      - name: stock
        in: formData
        type: integer
      - name: category_id
        in: formData
        type: integer
      - name: image
        in: formData
        type: file
    responses:
      200:
        description: Товар обновлен
      404:
        description: Товар не найден
    """
    try:
        product = Product.query.get(product_id)
        if not product:
            raise NotFoundError("Товар не найден")
        
        schema = ProductUpdateSchema()
        try:
            data = schema.load(request.form.to_dict())
        except MarshmallowValidationError as err:
            raise ValidationError(f"Ошибка валидации: {err.messages}")
        
        if "title" in data:
            product.title = data["title"]
        if "description" in data:
            product.description = data["description"]
        if "price" in data:
            product.price = data["price"]
        if "stock" in data:
            product.stock = data["stock"]
        if "category_id" in data:
            product.category_id = data["category_id"]
        if "brand_id" in data:
            product.brand_id = data["brand_id"] if data["brand_id"] else None
        
        # Обновление изображения
        if "image" in request.files:
            f = request.files["image"]
            if f.filename:
                saved = save_product_image(f)
                if saved is None:
                    raise ValidationError("Недопустимое расширение файла изображения")
                product.image = saved
        
        db.session.commit()
        
        # Очищаем кэш
        cache = current_app.cache
        cache.delete(f"product_{product_id}")
        cache.delete("categories_list")
        
        product_schema = ProductSchema()
        return jsonify({
            "success": True,
            "message": "Товар успешно обновлен",
            "product": product_schema.dump(product)
        }), 200
    except (ValidationError, NotFoundError) as e:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Ошибка при обновлении товара: {str(e)}")

@admin_bp.route("/products/<int:product_id>", methods=["DELETE"])
@admin_required
def delete_product(product_id):
    """
    Удалить товар
    ---
    tags:
      - admin
    security:
      - Bearer: []
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Товар удален
      404:
        description: Товар не найден
    """
    try:
        product = Product.query.get(product_id)
        if not product:
            raise NotFoundError("Товар не найден")
        
        db.session.delete(product)
        db.session.commit()
        
        # Очищаем кэш
        cache = current_app.cache
        cache.delete(f"product_{product_id}")
        cache.delete("categories_list")
        
        return jsonify({
            "success": True,
            "message": "Товар успешно удален"
        }), 200
    except NotFoundError as e:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Ошибка при удалении товара: {str(e)}")

@admin_bp.route("/orders", methods=["GET"])
@admin_required
def list_all_orders():
    """
    Получить список всех заказов (для админа)
    ---
    tags:
      - admin
    security:
      - Bearer: []
    responses:
      200:
        description: Список всех заказов
    """
    try:
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        query = Order.query.options(joinedload(Order.user), joinedload(Order.items).joinedload(OrderItem.product))
        
        if status:
            query = query.filter(Order.status == status)
        
        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=limit, error_out=False
        )
        
        order_schema = OrderSchema(many=True)
        
        return jsonify({
            "success": True,
            "orders": order_schema.dump(orders.items),
            "total": orders.total,
            "page": page,
            "totalPages": orders.pages
        }), 200
    except Exception as e:
        raise ValidationError(f"Ошибка при получении заказов: {str(e)}")

@admin_bp.route("/orders/<int:order_id>", methods=["GET"])
@admin_required
def get_order(order_id):
    """
    Получить детали заказа (для админа)
    ---
    tags:
      - admin
    security:
      - Bearer: []
    responses:
      200:
        description: Детали заказа
      404:
        description: Заказ не найден
    """
    try:
        order = Order.query.options(
            joinedload(Order.user),
            joinedload(Order.items).joinedload(OrderItem.product),
            joinedload(Order.history)
        ).get(order_id)
        
        if not order:
            raise NotFoundError("Заказ не найден")
        
        order_schema = OrderSchema()
        return jsonify({
            "success": True,
            "order": order_schema.dump(order)
        }), 200
    except NotFoundError as e:
        raise
    except Exception as e:
        raise ValidationError(f"Ошибка при получении заказа: {str(e)}")

@admin_bp.route("/orders/<int:order_id>/status", methods=["PUT"])
@admin_required
def update_order_status(order_id):
    """
    Обновить статус заказа (для админа)
    ---
    tags:
      - admin
    security:
      - Bearer: []
    responses:
      200:
        description: Статус заказа обновлен
      404:
        description: Заказ не найден
    """
    try:
        order = Order.query.get(order_id)
        if not order:
            raise NotFoundError("Заказ не найден")
        
        data = request.get_json() or {}
        new_status = data.get("status")
        comment = data.get("comment")
        
        if not new_status:
            raise ValidationError("Статус не указан")
        
        # Добавляем в историю
        admin_id = get_jwt_identity()
        history = OrderHistory(
            order_id=order_id,
            status=new_status,
            changed_by=str(admin_id),
            comment=comment
        )
        db.session.add(history)
        
        order.status = new_status
        db.session.commit()
        
        order_schema = OrderSchema()
        return jsonify({
            "success": True,
            "message": "Статус заказа обновлен",
            "order": order_schema.dump(order)
        }), 200
    except (NotFoundError, ValidationError) as e:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Ошибка при обновлении статуса: {str(e)}")

@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_all_users():
    """
    Получить список всех пользователей (для админа)
    ---
    tags:
      - admin
    security:
      - Bearer: []
    responses:
      200:
        description: Список всех пользователей
    """
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        
        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": user.role,
                "avatar": user.avatar,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "orders_count": len(user.orders) if user.orders else 0
            })
        
        return jsonify({
            "success": True,
            "users": users_data
        }), 200
    except Exception as e:
        raise ValidationError(f"Ошибка при получении пользователей: {str(e)}")

@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id):
    """
    Получить информацию о пользователе (для админа)
    ---
    tags:
      - admin
    security:
      - Bearer: []
    responses:
      200:
        description: Информация о пользователе
      404:
        description: Пользователь не найден
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        
        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "avatar": user.avatar,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "orders_count": len(user.orders) if user.orders else 0
        }
        
        return jsonify({
            "success": True,
            "user": user_data
        }), 200
    except NotFoundError as e:
        raise
    except Exception as e:
        raise ValidationError(f"Ошибка при получении пользователя: {str(e)}")

@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):
    """
    Обновить информацию о пользователе (для админа)
    ---
    tags:
      - admin
    security:
      - Bearer: []
    responses:
      200:
        description: Пользователь обновлен
      404:
        description: Пользователь не найден
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        
        data = request.get_json() or {}
        
        if "first_name" in data:
            user.first_name = data["first_name"]
        if "last_name" in data:
            user.last_name = data["last_name"]
        if "email" in data:
            # Проверяем уникальность email
            existing_user = User.query.filter(User.email == data["email"], User.id != user_id).first()
            if existing_user:
                raise ValidationError("Email уже используется")
            user.email = data["email"]
        if "role" in data:
            if data["role"] not in ["user", "admin"]:
                raise ValidationError("Недопустимая роль")
            user.role = data["role"]
        
        db.session.commit()
        
        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "avatar": user.avatar,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        
        return jsonify({
            "success": True,
            "message": "Пользователь успешно обновлен",
            "user": user_data
        }), 200
    except (NotFoundError, ValidationError) as e:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Ошибка при обновлении пользователя: {str(e)}")

@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """
    Удалить пользователя (для админа)
    ---
    tags:
      - admin
    security:
      - Bearer: []
    responses:
      200:
        description: Пользователь удален
      404:
        description: Пользователь не найден
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        
        # Нельзя удалить самого себя
        current_user_id = get_jwt_identity()
        if user.id == current_user_id:
            raise ValidationError("Нельзя удалить самого себя")
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Пользователь успешно удален"
        }), 200
    except (NotFoundError, ValidationError) as e:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Ошибка при удалении пользователя: {str(e)}")

@admin_bp.route("/stats", methods=["GET"])
@admin_required
def get_stats():
    """
    Получить статистику (для админа)
    ---
    tags:
      - admin
    security:
      - Bearer: []
    responses:
      200:
        description: Статистика
    """
    try:
        # Общее количество товаров
        total_products = Product.query.count()
        
        # Общее количество заказов
        total_orders = Order.query.count()
        
        # Общее количество пользователей
        total_users = User.query.count()
        
        # Общая сумма всех заказов
        total_revenue = db.session.query(func.sum(Order.total)).scalar() or 0
        
        # Заказы по статусам
        orders_by_status = db.session.query(
            Order.status,
            func.count(Order.id)
        ).group_by(Order.status).all()
        
        status_counts = {status: count for status, count in orders_by_status}
        
        # Товары с низким остатком (меньше 10)
        low_stock_products = Product.query.filter(Product.stock < 10).count()
        
        return jsonify({
            "success": True,
            "stats": {
                "total_products": total_products,
                "total_orders": total_orders,
                "total_users": total_users,
                "total_revenue": float(total_revenue),
                "orders_by_status": status_counts,
                "low_stock_products": low_stock_products
            }
        }), 200
    except Exception as e:
        raise ValidationError(f"Ошибка при получении статистики: {str(e)}")

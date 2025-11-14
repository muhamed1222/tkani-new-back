from flask import Blueprint, request, jsonify, make_response
import json
from models import Product
from errors import NotFoundError, ValidationError
from schemas import CartAddSchema, CartUpdateSchema, CartRemoveSchema
from marshmallow import ValidationError as MarshmallowValidationError
from sqlalchemy.orm import joinedload

cart_bp = Blueprint("cart", __name__)

def read_cart_from_cookie():
    """Читает корзину из cookie"""
    cart_cookie = request.cookies.get("cart")
    if not cart_cookie:
        return {}
    try:
        data = json.loads(cart_cookie)
        if isinstance(data, dict):
            return {int(k): int(v) for k, v in data.items()}
    except Exception:
        return {}
    return {}

def cart_response(cart_dict):
    """Формирует ответ с содержимым корзины"""
    items = []
    subtotal = 0.0
    
    # Оптимизация: загружаем все продукты одним запросом
    if cart_dict:
        product_ids = list(cart_dict.keys())
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        products_dict = {p.id: p for p in products}
    else:
        products_dict = {}
    
    for pid, qty in cart_dict.items():
        product = products_dict.get(pid)
        if not product:
            continue
        line = {
            "id": len(items) + 1,  # временный ID для элемента корзины
            "product_id": pid,
            "product": {
                "id": product.id,
                "title": product.title,
                "price": product.price,
                "image": product.image or "/placeholder-product.jpg"
            },
            "quantity": float(qty),  # поддерживаем дробное количество
            "total_price": round(product.price * qty, 2)
        }
        subtotal += product.price * qty
        items.append(line)
    
    return {
        "success": True,
        "items": items,
        "total": round(subtotal, 2),
        "total_items": len(items)
    }

@cart_bp.route("/", methods=["GET"])
def get_cart():
    """
    Получить содержимое корзины
    ---
    tags:
      - cart
    responses:
      200:
        description: Содержимое корзины
    """
    cart = read_cart_from_cookie()
    return jsonify(cart_response(cart)), 200

@cart_bp.route("/add", methods=["POST"])
def add_to_cart():
    """
    Добавить товар в корзину
    ---
    tags:
      - cart
    parameters:
      - name: product_id
        in: body
        type: integer
        required: true
      - name: quantity
        in: body
        type: integer
        default: 1
    responses:
      200:
        description: Товар добавлен в корзину
    """
    try:
        schema = CartAddSchema()
        try:
            data = schema.load(request.get_json() or {})
        except MarshmallowValidationError as err:
            raise ValidationError(f"Ошибка валидации: {err.messages}")
        
        pid = data["product_id"]
        qty = data.get("quantity", 1)
        
        product = Product.query.get(pid)
        if not product:
            raise NotFoundError("Товар не найден")
        
        cart = read_cart_from_cookie()
        current_qty = cart.get(pid, 0)
        new_qty = current_qty + qty
        
        # Проверка остатка
        if product.stock is not None and new_qty > product.stock:
            new_qty = product.stock
            if current_qty >= product.stock:
                raise ValidationError(f"Недостаточно товара на складе. Доступно: {product.stock}")
        
        cart[pid] = new_qty
        resp = make_response(jsonify(cart_response(cart)), 200)
        resp.set_cookie("cart", json.dumps(cart), httponly=False, samesite="Lax", max_age=86400*30)  # 30 дней
        return resp
    except (ValidationError, NotFoundError) as e:
        raise
    except Exception as e:
        raise ValidationError(f"Ошибка при добавлении в корзину: {str(e)}")

@cart_bp.route("/remove", methods=["POST"])
def remove_from_cart():
    """
    Удалить товар из корзины
    ---
    tags:
      - cart
    parameters:
      - name: product_id
        in: body
        type: integer
        required: true
    responses:
      200:
        description: Товар удален из корзины
    """
    try:
        schema = CartRemoveSchema()
        try:
            data = schema.load(request.get_json() or {})
        except MarshmallowValidationError as err:
            raise ValidationError(f"Ошибка валидации: {err.messages}")
        
        pid = data["product_id"]
        cart = read_cart_from_cookie()
        
        if pid in cart:
            cart.pop(pid)
        
        resp = make_response(jsonify(cart_response(cart)), 200)
        resp.set_cookie("cart", json.dumps(cart), httponly=False, samesite="Lax", max_age=86400*30)
        return resp
    except ValidationError as e:
        raise
    except Exception as e:
        raise ValidationError(f"Ошибка при удалении из корзины: {str(e)}")

@cart_bp.route("/update", methods=["POST"])
def update_cart():
    """
    Обновить количество товара в корзине
    ---
    tags:
      - cart
    parameters:
      - name: product_id
        in: body
        type: integer
        required: true
      - name: quantity
        in: body
        type: integer
        required: true
    responses:
      200:
        description: Количество обновлено
    """
    try:
        schema = CartUpdateSchema()
        try:
            data = schema.load(request.get_json() or {})
        except MarshmallowValidationError as err:
            raise ValidationError(f"Ошибка валидации: {err.messages}")
        
        pid = data["product_id"]
        qty = data["quantity"]
        
        product = Product.query.get(pid)
        if not product:
            raise NotFoundError("Товар не найден")
        
        cart = read_cart_from_cookie()
        
        if qty <= 0:
            cart.pop(pid, None)
        else:
            # Проверка остатка
            if product.stock is not None and qty > product.stock:
                qty = product.stock
                raise ValidationError(f"Недостаточно товара на складе. Доступно: {product.stock}")
            cart[pid] = qty
        
        resp = make_response(jsonify(cart_response(cart)), 200)
        resp.set_cookie("cart", json.dumps(cart), httponly=False, samesite="Lax", max_age=86400*30)
        return resp
    except (ValidationError, NotFoundError) as e:
        raise
    except Exception as e:
        raise ValidationError(f"Ошибка при обновлении корзины: {str(e)}")

@cart_bp.route("/clear", methods=["POST"])
def clear_cart():
    """
    Очистить корзину
    ---
    tags:
      - cart
    responses:
      200:
        description: Корзина очищена
    """
    resp = make_response(jsonify({
        "success": True,
        "message": "Корзина очищена",
        "items": [],
        "subtotal": 0,
        "total": 0,
        "count": 0
    }), 200)
    resp.set_cookie("cart", "", expires=0)
    return resp

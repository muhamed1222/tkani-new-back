from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, OrderItem, OrderHistory, Product, User
from routes.cart import read_cart_from_cookie
from errors import NotFoundError, ValidationError
from schemas import OrderSchema
from sqlalchemy.orm import joinedload

orders_bp = Blueprint("orders", __name__)

def add_order_history(order_id, status, changed_by="system", comment=None):
    """Добавить запись в историю заказа"""
    history = OrderHistory(
        order_id=order_id,
        status=status,
        changed_by=str(changed_by),
        comment=comment
    )
    db.session.add(history)

@orders_bp.route("/create", methods=["POST"])
@jwt_required()
def create_order():
    """
    Создать заказ из корзины
    ---
    tags:
      - orders
    security:
      - Bearer: []
    responses:
      201:
        description: Заказ успешно создан
      400:
        description: Корзина пуста
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        
        cart = read_cart_from_cookie()
        if not cart:
            raise ValidationError("Корзина пуста")

        # Получаем дополнительные данные из запроса
        data = request.get_json() or {}
        delivery_address = data.get("delivery_address")
        phone = data.get("phone")
        comment = data.get("comment")

        total = 0.0
        items = []
        for pid, qty in cart.items():
            product = Product.query.get(pid)
            if not product:
                continue
            if product.stock is not None and qty > product.stock:
                qty = product.stock
            if qty <= 0:
                continue
            line_total = product.price * qty
            total += line_total
            items.append((product, qty, product.price))

        if not items:
            raise ValidationError("Нет валидных товаров для заказа")

        # Создаем заказ (пока без delivery_address и phone в модели, можно добавить позже)
        order = Order(user_id=user_id, total=round(total, 2), status="pending")
        db.session.add(order)
        db.session.flush()  # получить id

        for product, qty, price in items:
            oi = OrderItem(order_id=order.id, product_id=product.id, quantity=qty, price=price)
            db.session.add(oi)
            # уменьшить stock если нужно
            if product.stock is not None:
                product.stock = max(0, product.stock - qty)
        
        # Добавляем запись в историю с комментарием
        history_comment = "Заказ создан"
        if delivery_address:
            history_comment += f". Адрес доставки: {delivery_address}"
        if phone:
            history_comment += f". Телефон: {phone}"
        if comment:
            history_comment += f". Комментарий: {comment}"
        
        add_order_history(order.id, "pending", changed_by=user_id, comment=history_comment)
        
        db.session.commit()

        # Загружаем заказ с полными данными для ответа
        order = Order.query.options(
            joinedload(Order.items).joinedload(OrderItem.product)
        ).get(order.id)
        
        order_schema = OrderSchema()
        
        # Очистить cookie корзины
        resp = jsonify({
            "success": True,
            "order": order_schema.dump(order)
        })
        resp.set_cookie("cart", "", expires=0)
        return resp, 201
    except (ValidationError, NotFoundError) as e:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Ошибка при создании заказа: {str(e)}")

@orders_bp.route("/my", methods=["GET"])
@jwt_required()
def my_orders():
    """
    Получить список заказов текущего пользователя
    ---
    tags:
      - orders
    security:
      - Bearer: []
    parameters:
      - name: status
        in: query
        type: string
        enum: [pending, processing, shipped, delivered, cancelled]
      - name: page
        in: query
        type: integer
        default: 1
      - name: limit
        in: query
        type: integer
        default: 10
    responses:
      200:
        description: Список заказов
    """
    try:
        user_id = get_jwt_identity()
        
        # Получаем параметры запроса
        status = request.args.get("status")
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        
        # Формируем запрос
        query = Order.query.filter_by(user_id=user_id)
        
        # Фильтр по статусу
        if status:
            query = query.filter_by(status=status)
        
        # Пагинация
        pagination = query.order_by(Order.created_at.desc()).paginate(
            page=page,
            per_page=limit,
            error_out=False
        )
        
        # Формируем упрощенный список заказов
        orders_list = []
        for order in pagination.items:
            orders_list.append({
                "id": order.id,
                "status": order.status,
                "total": order.total,
                "items_count": len(order.items),
                "created_at": order.created_at.isoformat() if order.created_at else None
            })
        
        result = {
            "success": True,
            "orders": orders_list,
            "total": pagination.total,
            "page": page,
            "totalPages": pagination.pages
        }
        
        return jsonify(result), 200
    except Exception as e:
        raise ValidationError(f"Ошибка при получении заказов: {str(e)}")

@orders_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    """
    Получить детали заказа
    ---
    tags:
      - orders
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Детали заказа
      404:
        description: Заказ не найден
    """
    try:
        user_id = get_jwt_identity()
        
        # Оптимизация: eager loading
        order = Order.query.options(
            joinedload(Order.items).joinedload(OrderItem.product),
            joinedload(Order.history)
        ).filter_by(id=order_id, user_id=user_id).first()
        
        if not order:
            raise NotFoundError("Заказ не найден")
        
        order_schema = OrderSchema()
        result = {
            "success": True,
            "order": order_schema.dump(order),
            "history": [
                {
                    "id": h.id,
                    "status": h.status,
                    "changed_by": h.changed_by,
                    "comment": h.comment,
                    "created_at": h.created_at.isoformat()
                }
                for h in order.history
            ]
        }
        
        return jsonify(result), 200
    except (NotFoundError, ValidationError) as e:
        raise
    except Exception as e:
        raise ValidationError(f"Ошибка при получении заказа: {str(e)}")

@orders_bp.route("/<int:order_id>/status", methods=["PUT"])
@jwt_required()
def update_order_status(order_id):
    """
    Обновить статус заказа (только для админов или владельца заказа)
    ---
    tags:
      - orders
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
      - name: status
        in: body
        type: string
        required: true
        enum: [created, paid, shipped, cancelled]
      - name: comment
        in: body
        type: string
    responses:
      200:
        description: Статус обновлен
      403:
        description: Доступ запрещен
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        
        order = Order.query.get(order_id)
        if not order:
            raise NotFoundError("Заказ не найден")
        
        # Проверка прав: только владелец заказа или админ
        if order.user_id != int(user_id) and user.role != "admin":
            from errors import ForbiddenError
            raise ForbiddenError("У вас нет прав для изменения этого заказа")
        
        data = request.get_json() or {}
        new_status = data.get("status")
        comment = data.get("comment")
        
        if not new_status:
            raise ValidationError("Статус не указан")
        
        valid_statuses = ["created", "paid", "shipped", "cancelled"]
        if new_status not in valid_statuses:
            raise ValidationError(f"Недопустимый статус. Допустимые: {', '.join(valid_statuses)}")
        
        old_status = order.status
        order.status = new_status
        
        # Добавляем запись в историю
        add_order_history(
            order.id,
            new_status,
            changed_by=user_id,
            comment=comment or f"Статус изменен с '{old_status}' на '{new_status}'"
        )
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Статус заказа обновлен",
            "order_id": order.id,
            "status": new_status
        }), 200
    except (ValidationError, NotFoundError) as e:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Ошибка при обновлении статуса: {str(e)}")

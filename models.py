from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False, index=True)
    last_name = db.Column(db.String(120), nullable=False, index=True)
    email = db.Column(db.String(200), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(300))  # путь к файлу в static/avatars
    role = db.Column(db.String(20), default="user", index=True)  # user, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    orders = db.relationship("Order", backref="user", lazy=True)
    
    __table_args__ = (
        db.Index('idx_user_email', 'email'),
        db.Index('idx_user_role', 'role'),
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    products = db.relationship("Product", backref="category", lazy=True)
    
    __table_args__ = (
        db.Index('idx_category_name', 'name'),
    )

class Brand(db.Model):
    """Бренды товаров"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    products = db.relationship("Product", backref="brand", lazy=True)
    
    __table_args__ = (
        db.Index('idx_brand_name', 'name'),
        db.Index('idx_brand_slug', 'slug'),
    )

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False, index=True)
    stock = db.Column(db.Integer, default=0, index=True)
    image = db.Column(db.String(300))  # путь или URL (основное изображение)
    images = db.Column(db.Text)  # JSON массив дополнительных изображений
    specifications = db.Column(db.Text)  # JSON объект с характеристиками
    rating = db.Column(db.Float, default=0.0)  # средний рейтинг
    reviews_count = db.Column(db.Integer, default=0)  # количество отзывов
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True, index=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brand.id"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_product_title', 'title'),
        db.Index('idx_product_price', 'price'),
        db.Index('idx_product_category', 'category_id'),
        db.Index('idx_product_brand', 'brand_id'),
        db.Index('idx_product_stock', 'stock'),
    )

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    total = db.Column(db.Float, nullable=False)
    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")
    status = db.Column(db.String(50), default="created", index=True)  # created, paid, shipped, cancelled
    history = db.relationship("OrderHistory", backref="order", lazy=True, cascade="all, delete-orphan")
    
    __table_args__ = (
        db.Index('idx_order_user', 'user_id'),
        db.Index('idx_order_status', 'status'),
        db.Index('idx_order_created', 'created_at'),
    )

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # price at time of order
    product = db.relationship("Product")
    
    __table_args__ = (
        db.Index('idx_orderitem_order', 'order_id'),
        db.Index('idx_orderitem_product', 'product_id'),
    )

class OrderHistory(db.Model):
    """История изменений заказа"""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False)
    changed_by = db.Column(db.String(200))  # user_id или 'system'
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        db.Index('idx_orderhistory_order', 'order_id'),
        db.Index('idx_orderhistory_created', 'created_at'),
    )

class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False, index=True)
    image = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(500), default='#')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_work_created', 'created_at'),
    )

class PasswordResetCode(db.Model):
    """Коды восстановления пароля"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False, index=True)
    code = db.Column(db.String(6), nullable=False)  # 6-значный код
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    used = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        db.Index('idx_resetcode_email', 'email'),
        db.Index('idx_resetcode_expires', 'expires_at'),
        db.Index('idx_resetcode_used', 'used'),
    )
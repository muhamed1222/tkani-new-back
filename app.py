import os
from flask import Flask
from config import Config
from models import db
from flask_jwt_extended import JWTManager
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app, supports_credentials=True)  # разрешаем куки/credentials если фронтенд с другим origin

    # импорт и регистрация роутов
    from routes.auth import auth_bp
    from routes.catalog import catalog_bp
    from routes.cart import cart_bp
    from routes.orders import orders_bp
    from routes.admin import admin_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(catalog_bp, url_prefix="/api/catalog")
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # создать БД если не существует
    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
import os
from flask import Flask
from config import Config
from models import db
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flasgger import Swagger
from errors import register_error_handlers

# Загружаем переменные окружения из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv не установлен, используем системные переменные окружения

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Выбираем конфигурацию
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    from config import config as app_config
    app.config.from_object(app_config[config_name])
    
    # Проверка для production конфигурации
    if config_name == 'production':
        if not app.config.get('SECRET_KEY') or app.config.get('SECRET_KEY') == "dev-secret-key-change-in-production":
            raise ValueError("SECRET_KEY must be set in production environment")
        if not app.config.get('JWT_SECRET_KEY') or app.config.get('JWT_SECRET_KEY') == "jwt-secret-string-change-in-production":
            raise ValueError("JWT_SECRET_KEY must be set in production environment")
        
        # Предупреждение о SQLite в production
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'sqlite' in db_url:
            import warnings
            warnings.warn("SQLite is not recommended for production. Use PostgreSQL instead.")
    
    # Создаем необходимые директории
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PRODUCTS_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['WORKS_UPLOAD_FOLDER'], exist_ok=True)

    # Инициализация расширений
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # JWT
    jwt = JWTManager(app)
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)
    
    # CORS
    CORS(app, supports_credentials=True)
    
    # Rate Limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[app.config.get('RATELIMIT_DEFAULT', '200 per hour')],
        storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://')
    )
    app.limiter = limiter
    
    # Caching
    cache_config = app.config.get('CACHE_CONFIG', {
        'CACHE_TYPE': app.config.get('CACHE_TYPE', 'SimpleCache'),
        'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
    })
    cache = Cache(app, config=cache_config)
    app.cache = cache
    
    # Swagger/OpenAPI документация
    swagger = Swagger(app, config=app.config.get('SWAGGER', {}))
    
    # Регистрация обработчиков ошибок
    register_error_handlers(app)

    # Импорт и регистрация роутов с версионированием
    api_version = app.config.get('API_VERSION', 'v1')
    api_prefix = f"/api/{api_version}"
    
    from routes import auth, catalog, cart, orders, admin, works
    
    app.register_blueprint(auth.auth_bp, url_prefix=f"{api_prefix}/auth")
    app.register_blueprint(catalog.catalog_bp, url_prefix=f"{api_prefix}/catalog")
    app.register_blueprint(cart.cart_bp, url_prefix=f"{api_prefix}/cart")
    app.register_blueprint(orders.orders_bp, url_prefix=f"{api_prefix}/orders")
    app.register_blueprint(admin.admin_bp, url_prefix=f"{api_prefix}/admin")
    app.register_blueprint(works.works_bp, url_prefix=f"{api_prefix}")
    
    # Обратная совместимость - старые маршруты без версии
    app.register_blueprint(auth.auth_bp, url_prefix="/api/auth", name="auth_legacy")
    app.register_blueprint(catalog.catalog_bp, url_prefix="/api/catalog", name="catalog_legacy")
    app.register_blueprint(cart.cart_bp, url_prefix="/api/cart", name="cart_legacy")
    app.register_blueprint(orders.orders_bp, url_prefix="/api/orders", name="orders_legacy")
    app.register_blueprint(admin.admin_bp, url_prefix="/api/admin", name="admin_legacy")
    app.register_blueprint(works.works_bp, url_prefix="/api", name="works_legacy")

    # Создать БД если не существует (только для разработки)
    # В production используйте миграции: flask db upgrade
    with app.app_context():
        if os.environ.get('FLASK_ENV') == 'development':
            db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, port=port)
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO", "False").lower() == "true"
    
    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-string-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))  # 1 час по умолчанию
    JWT_ALGORITHM = "HS256"
    
    # File Uploads
    UPLOAD_FOLDER = os.path.join(basedir, "static", "avatars")
    PRODUCTS_UPLOAD_FOLDER = os.path.join(basedir, "static", "products")
    WORKS_UPLOAD_FOLDER = os.path.join(basedir, "static", "works")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", "memory://")
    RATELIMIT_DEFAULT = os.environ.get("RATELIMIT_DEFAULT", "200 per hour")
    RATELIMIT_AUTH = os.environ.get("RATELIMIT_AUTH", "5 per minute")
    
    # Caching
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", 300))  # 5 минут
    CACHE_REDIS_URL = os.environ.get("CACHE_REDIS_URL", None)
    
    # Если используется Redis для кэширования
    if CACHE_TYPE == "RedisCache" and CACHE_REDIS_URL:
        CACHE_CONFIG = {
            'CACHE_TYPE': 'RedisCache',
            'CACHE_REDIS_URL': CACHE_REDIS_URL,
            'CACHE_DEFAULT_TIMEOUT': CACHE_DEFAULT_TIMEOUT
        }
    else:
        CACHE_CONFIG = {
            'CACHE_TYPE': CACHE_TYPE,
            'CACHE_DEFAULT_TIMEOUT': CACHE_DEFAULT_TIMEOUT
        }
    
    # API
    API_VERSION = "v1"
    API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5001")
    
    # Swagger/OpenAPI
    SWAGGER = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apispec/",
        "title": "Tkani API",
        "version": "1.0.0",
        "description": "REST API для интернет-магазина тканей",
        "basePath": "/api/v1",
        "schemes": ["http", "https"],
        "tags": [
            {"name": "auth", "description": "Аутентификация и авторизация"},
            {"name": "catalog", "description": "Каталог товаров"},
            {"name": "cart", "description": "Корзина покупок"},
            {"name": "orders", "description": "Заказы"},
            {"name": "admin", "description": "Административные функции"},
            {"name": "works", "description": "Портфолио работ"}
        ]
    }

class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    FLASK_ENV = "development"

class ProductionConfig(Config):
    """Конфигурация для production"""
    DEBUG = False
    FLASK_ENV = "production"

# Выбор конфигурации на основе переменной окружения
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

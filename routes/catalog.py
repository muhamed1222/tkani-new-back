from flask import Blueprint, request, jsonify, current_app
from models import db, Product, Category, Brand
from sqlalchemy import or_
from errors import NotFoundError, ValidationError
from schemas import ProductListQuerySchema, ProductSchema, CategorySchema
from flask_caching import Cache
from marshmallow import ValidationError as MarshmallowValidationError
import json as json_lib

catalog_bp = Blueprint("catalog", __name__)

@catalog_bp.route("/products", methods=["GET"])
def list_products():
    """
    Получить список товаров с фильтрацией, поиском и пагинацией
    ---
    tags:
      - catalog
    parameters:
      - name: q
        in: query
        type: string
        description: Поиск по названию и описанию
      - name: category
        in: query
        type: integer
        description: ID категории
      - name: categories
        in: query
        type: string
        description: Список ID категорий через запятую (например, "1,2,3")
      - name: min_price
        in: query
        type: number
        description: Минимальная цена
      - name: max_price
        in: query
        type: number
        description: Максимальная цена
      - name: sort
        in: query
        type: string
        enum: [price_asc, price_desc, title_asc, title_desc, id_desc]
        default: id_desc
      - name: page
        in: query
        type: integer
        default: 1
      - name: per_page
        in: query
        type: integer
        default: 12
    responses:
      200:
        description: Список товаров
    """
    try:
        # Валидация параметров
        schema = ProductListQuerySchema()
        try:
            params = schema.load(request.args.to_dict())
        except MarshmallowValidationError as err:
            raise ValidationError(f"Ошибка валидации параметров: {err.messages}")
        
        q = params.get("q")
        category = params.get("category")
        categories_str = request.args.get("categories", type=str)  # Множественный выбор категорий
        min_price = params.get("min_price")
        max_price = params.get("max_price")
        sort = params.get("sort", "id_desc")
        page = params.get("page", 1)
        per_page = params.get("per_page", 12)

        # Кэширование ключа
        cache_key = f"products_{q}_{category}_{categories_str}_{min_price}_{max_price}_{sort}_{page}_{per_page}"
        cache = current_app.cache
        
        # Проверяем кэш
        cached_result = cache.get(cache_key)
        if cached_result:
            return jsonify(cached_result), 200

        query = Product.query

        # Расширенный поиск по названию и описанию
        if q:
            query = query.filter(
                or_(
                    Product.title.ilike(f"%{q}%"),
                    Product.description.ilike(f"%{q}%")
                )
            )
        
        # Фильтр по одной категории
        if category:
            query = query.filter_by(category_id=category)
        
        # Фильтр по нескольким категориям
        if categories_str:
            try:
                category_ids = [int(cid.strip()) for cid in categories_str.split(",")]
                query = query.filter(Product.category_id.in_(category_ids))
            except ValueError:
                raise ValidationError("Некорректный формат списка категорий")
        
        # Фильтр по бренду
        brand_id = request.args.get("brand_id", type=int)
        if brand_id:
            query = query.filter(Product.brand_id == brand_id)
        
        # Фильтры по цене
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        # Сортировка
        if sort == "price_asc":
            query = query.order_by(Product.price.asc())
        elif sort == "price_desc":
            query = query.order_by(Product.price.desc())
        elif sort == "title_asc":
            query = query.order_by(Product.title.asc())
        elif sort == "title_desc":
            query = query.order_by(Product.title.desc())
        elif sort == "newest":
            query = query.order_by(Product.created_at.desc())
        else:
            query = query.order_by(Product.id.desc())

        # Пагинация
        pag = query.paginate(page=page, per_page=per_page, error_out=False)
        
        product_schema = ProductSchema(many=True)
        items = product_schema.dump(pag.items)

        result = {
            "success": True,
            "items": items,
            "total": pag.total,
            "page": pag.page,
            "pages": pag.pages
        }
        
        # Кэшируем результат на 5 минут
        cache.set(cache_key, result, timeout=300)
        
        return jsonify(result), 200
    except (ValidationError, NotFoundError) as e:
        raise
    except Exception as e:
        raise ValidationError(f"Ошибка при получении списка товаров: {str(e)}")

@catalog_bp.route("/categories", methods=["GET"])
def list_categories():
    """
    Получить список категорий
    ---
    tags:
      - catalog
    responses:
      200:
        description: Список категорий
    """
    try:
        cache = current_app.cache
        cache_key = "categories_list"
        
        # Проверяем кэш
        cached_result = cache.get(cache_key)
        if cached_result:
            return jsonify(cached_result), 200
        
        cats = Category.query.all()
        category_schema = CategorySchema(many=True)
        result = {
            "success": True,
            "categories": category_schema.dump(cats)
        }
        
        # Кэшируем на 1 час (категории редко меняются)
        cache.set(cache_key, result, timeout=3600)
        
        return jsonify(result), 200
    except Exception as e:
        raise ValidationError(f"Ошибка при получении категорий: {str(e)}")

@catalog_bp.route("/brands", methods=["GET"])
def list_brands():
    """
    Получить список брендов
    ---
    tags:
      - catalog
    responses:
      200:
        description: Список брендов
    """
    try:
        cache = current_app.cache
        cache_key = "brands_list"
        
        # Проверяем кэш
        cached_result = cache.get(cache_key)
        if cached_result:
            return jsonify(cached_result), 200
        
        brands = Brand.query.order_by(Brand.name.asc()).all()
        brands_list = [
            {
                "id": brand.id,
                "name": brand.name,
                "slug": brand.slug
            }
            for brand in brands
        ]
        
        result = {
            "success": True,
            "brands": brands_list
        }
        
        # Кэшируем на 1 час (бренды редко меняются)
        cache.set(cache_key, result, timeout=3600)
        
        return jsonify(result), 200
    except Exception as e:
        raise ValidationError(f"Ошибка при получении брендов: {str(e)}")

@catalog_bp.route("/products/<int:product_id>", methods=["GET"])
def product_detail(product_id):
    """
    Получить детали товара
    ---
    tags:
      - catalog
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Детали товара
      404:
        description: Товар не найден
    """
    try:
        cache = current_app.cache
        cache_key = f"product_{product_id}"
        
        # Проверяем кэш
        cached_result = cache.get(cache_key)
        if cached_result:
            return jsonify(cached_result), 200
        
        product = Product.query.get(product_id)
        if not product:
            raise NotFoundError("Товар не найден")
        
        # Парсим JSON поля
        import json as json_lib
        images = []
        if product.images:
            try:
                images = json_lib.loads(product.images)
            except:
                images = []
        
        specifications = {}
        if product.specifications:
            try:
                specifications = json_lib.loads(product.specifications)
            except:
                specifications = {}
        
        # Формируем массив изображений (основное + дополнительные)
        all_images = [product.image] if product.image else []
        if images:
            all_images.extend(images)
        # Убираем дубликаты
        all_images = list(dict.fromkeys(all_images))
        
        # Получаем категорию
        category_data = None
        if product.category:
            category_data = {
                "id": product.category.id,
                "name": product.category.name
            }
        
        # Получаем похожие товары (из той же категории, исключая текущий)
        related_products = []
        if product.category_id:
            related = Product.query.filter(
                Product.category_id == product.category_id,
                Product.id != product_id
            ).limit(4).all()
            
            api_base_url = current_app.config.get('API_BASE_URL', 'http://localhost:5001')
            for rel_product in related:
                related_products.append({
                    "id": rel_product.id,
                    "title": rel_product.title,
                    "price": rel_product.price,
                    "image": rel_product.image or "/placeholder-product.jpg"
                })
        
        # Формируем ответ
        product_data = {
            "id": product.id,
            "title": product.title,
            "description": product.description,
            "price": product.price,
            "image": product.image or "/placeholder-product.jpg",
            "images": all_images,
            "category_id": product.category_id,
            "category": category_data,
            "stock": product.stock,
            "rating": product.rating or 5.0,
            "reviews_count": product.reviews_count or 0,
            "specifications": specifications,
            "related_products": related_products,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None
        }
        
        result = {
            "success": True,
            "product": product_data
        }
        
        # Кэшируем на 5 минут
        cache.set(cache_key, result, timeout=300)
        
        return jsonify(result), 200
    except (NotFoundError, ValidationError) as e:
        raise
    except Exception as e:
        raise ValidationError(f"Ошибка при получении товара: {str(e)}")

from flask import Blueprint, request, jsonify, send_from_directory, current_app
from models import db, Work
from sqlalchemy import desc
from errors import NotFoundError, ValidationError
from schemas import WorksListQuerySchema, WorkSchema
from marshmallow import ValidationError as MarshmallowValidationError
from flask_caching import Cache
import os

works_bp = Blueprint("works", __name__)

@works_bp.route("/works", methods=["GET"])
def get_works():
    """
    Получить список работ с пагинацией
    ---
    tags:
      - works
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
      - name: limit
        in: query
        type: integer
        default: 12
    responses:
      200:
        description: Список работ
    """
    try:
        # Валидация параметров
        schema = WorksListQuerySchema()
        try:
            params = schema.load(request.args.to_dict())
        except MarshmallowValidationError as err:
            raise ValidationError(f"Ошибка валидации параметров: {err.messages}")
        
        page = params.get("page", 1)
        limit = params.get("limit", 12)
        
        # Кэширование
        cache = current_app.cache
        cache_key = f"works_{page}_{limit}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return jsonify(cached_result), 200
        
        # Получаем работы с пагинацией
        pagination = Work.query.order_by(desc(Work.created_at)).paginate(
            page=page,
            per_page=limit,
            error_out=False
        )
        
        # Формируем список работ
        api_base_url = current_app.config.get('API_BASE_URL', 'http://localhost:5001')
        api_version = current_app.config.get('API_VERSION', 'v1')
        
        works = []
        for work in pagination.items:
            # Формируем URL изображения
            if work.image.startswith('/'):
                image_path = work.image.lstrip('/')
                if image_path.startswith('uploads/works/') or image_path.startswith('static/works/'):
                    filename = os.path.basename(image_path)
                    image_url = f"{api_base_url}/api/{api_version}/works/image/{filename}"
                else:
                    image_url = f"{api_base_url}{work.image}"
            elif work.image.startswith('static/'):
                filename = os.path.basename(work.image)
                image_url = f"{api_base_url}/api/{api_version}/works/image/{filename}"
            else:
                image_url = f"{api_base_url}/api/{api_version}/works/image/{work.image}"
            
            works.append({
                "id": work.id,
                "title": work.title,
                "image": image_url,
                "link": work.link,
                "created_at": work.created_at.isoformat() if work.created_at else None
            })
        
        result = {
            "success": True,
            "works": works,
            "total": pagination.total,
            "page": page,
            "totalPages": pagination.pages
        }
        
        # Кэшируем на 5 минут
        cache.set(cache_key, result, timeout=300)
        
        return jsonify(result), 200
        
    except ValidationError as e:
        raise
    except Exception as e:
        raise ValidationError(f"Ошибка при получении работ: {str(e)}")

@works_bp.route("/works/image/<filename>", methods=["GET"])
def get_work_image(filename):
    """
    Получить изображение работы
    ---
    tags:
      - works
    parameters:
      - name: filename
        in: path
        type: string
        required: true
    responses:
      200:
        description: Изображение
      404:
        description: Изображение не найдено
    """
    try:
        works_folder = current_app.config.get('WORKS_UPLOAD_FOLDER')
        if not works_folder:
            basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            works_folder = os.path.join(basedir, "static", "works")
        
        # Проверяем, существует ли файл
        file_path = os.path.join(works_folder, filename)
        if not os.path.exists(file_path):
            raise NotFoundError(f"Изображение не найдено: {filename}")
        
        return send_from_directory(works_folder, filename)
    except NotFoundError as e:
        raise
    except Exception as e:
        raise NotFoundError(f"Ошибка при получении изображения: {str(e)}")

@works_bp.route("/works/<int:work_id>", methods=["GET"])
def get_work_by_id(work_id):
    """
    Получить работу по ID
    ---
    tags:
      - works
    parameters:
      - name: work_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Работа
      404:
        description: Работа не найдена
    """
    try:
        work = Work.query.get_or_404(work_id)
        
        # Формируем URL изображения
        api_base_url = current_app.config.get('API_BASE_URL', 'http://localhost:5001')
        api_version = current_app.config.get('API_VERSION', 'v1')
        
        if work.image.startswith('/'):
            image_path = work.image.lstrip('/')
            if image_path.startswith('uploads/works/') or image_path.startswith('static/works/'):
                filename = os.path.basename(image_path)
                image_url = f"{api_base_url}/api/{api_version}/works/image/{filename}"
            else:
                image_url = f"{api_base_url}{work.image}"
        elif work.image.startswith('static/'):
            filename = os.path.basename(work.image)
            image_url = f"{api_base_url}/api/{api_version}/works/image/{filename}"
        else:
            image_url = f"{api_base_url}/api/{api_version}/works/image/{work.image}"
        
        result = {
            "success": True,
            "id": work.id,
            "title": work.title,
            "image": image_url,
            "link": work.link,
            "created_at": work.created_at.isoformat() if work.created_at else None
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        raise NotFoundError(f"Работа не найдена: {str(e)}")

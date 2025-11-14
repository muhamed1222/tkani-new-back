from flask import Blueprint, request, jsonify, send_from_directory, current_app
from models import db, Work
from sqlalchemy import desc
import os

works_bp = Blueprint("works", __name__)

@works_bp.route("/works", methods=["GET"])
def get_works():
    try:
        # Получаем параметры пагинации
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 12))
        
        # Валидация параметров
        if page < 1:
            page = 1
        if limit < 1:
            limit = 12
        
        # Получаем работы с пагинацией, сортировка по дате создания (новые первые)
        pagination = Work.query.order_by(desc(Work.created_at)).paginate(
            page=page,
            per_page=limit,
            error_out=False
        )
        
        # Формируем список работ
        # Преобразуем пути к изображениям в полные URL
        # Используем явный localhost:5001 или берем из переменной окружения
        api_base_url = os.environ.get('API_BASE_URL', 'http://localhost:5001')
        works = []
        for work in pagination.items:
            # Если путь начинается с /, используем его как есть, иначе добавляем /static/uploads/works/
            if work.image.startswith('/'):
                # Убираем начальный / и формируем URL
                image_path = work.image.lstrip('/')
                # Если путь начинается с uploads/works, используем endpoint для изображений
                if image_path.startswith('uploads/works/'):
                    filename = os.path.basename(image_path)
                    image_url = f"{api_base_url}/api/works/image/{filename}"
                else:
                    image_url = f"{api_base_url}{work.image}"
            else:
                image_url = f"{api_base_url}/static/uploads/works/{work.image}"
            
            works.append({
                "id": work.id,
                "title": work.title,
                "image": image_url,
                "link": work.link
            })
        
        return jsonify({
            "works": works,
            "total": pagination.total,
            "page": page,
            "totalPages": pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Ошибка при получении работ",
            "message": str(e)
        }), 500

@works_bp.route("/works/image/<filename>", methods=["GET"])
def get_work_image(filename):
    """Endpoint для обслуживания изображений работ"""
    try:
        # Путь к папке с изображениями работ
        basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        works_folder = os.path.join(basedir, "static", "works")
        
        # Проверяем, существует ли файл
        file_path = os.path.join(works_folder, filename)
        if not os.path.exists(file_path):
            # Если файл не найден, возвращаем 404 с правильными заголовками
            from flask import Response
            return Response(
                jsonify({"error": "Image not found", "filename": filename}).get_data(),
                status=404,
                mimetype='application/json'
            )
        
        return send_from_directory(works_folder, filename)
    except Exception as e:
        # Если файл не найден, возвращаем 404
        return jsonify({"error": "Image not found", "message": str(e)}), 404


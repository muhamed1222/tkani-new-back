from flask import Blueprint, request, jsonify
from models import db, Work
from sqlalchemy import desc

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
        works = [{
            "id": work.id,
            "title": work.title,
            "image": work.image,
            "link": work.link
        } for work in pagination.items]
        
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


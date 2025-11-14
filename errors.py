"""
Централизованная обработка ошибок API
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException

class APIError(Exception):
    """Базовый класс для ошибок API"""
    status_code = 400
    message = "Произошла ошибка"

    def __init__(self, message=None, status_code=None, payload=None):
        Exception.__init__(self)
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = True
        rv['message'] = self.message
        return rv

class ValidationError(APIError):
    """Ошибка валидации данных"""
    status_code = 400

class NotFoundError(APIError):
    """Ресурс не найден"""
    status_code = 404

class UnauthorizedError(APIError):
    """Не авторизован"""
    status_code = 401

class ForbiddenError(APIError):
    """Доступ запрещен"""
    status_code = 403

class ConflictError(APIError):
    """Конфликт данных"""
    status_code = 409

class InternalServerError(APIError):
    """Внутренняя ошибка сервера"""
    status_code = 500

def register_error_handlers(app):
    """Регистрация обработчиков ошибок"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        response = jsonify({
            'error': True,
            'message': error.description
        })
        response.status_code = error.code
        return response

    @app.errorhandler(404)
    def handle_not_found(error):
        response = jsonify({
            'error': True,
            'message': 'Ресурс не найден'
        })
        response.status_code = 404
        return response

    @app.errorhandler(500)
    def handle_internal_error(error):
        response = jsonify({
            'error': True,
            'message': 'Внутренняя ошибка сервера'
        })
        response.status_code = 500
        return response

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        # В production режиме не показываем детали ошибки
        import os
        if os.environ.get('FLASK_ENV') == 'development':
            message = str(error)
        else:
            message = 'Внутренняя ошибка сервера'
        
        response = jsonify({
            'error': True,
            'message': message
        })
        response.status_code = 500
        return response


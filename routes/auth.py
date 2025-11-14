from flask import Blueprint, request, jsonify, current_app, send_from_directory
from models import db, User, PasswordResetCode
from routes.utils import save_avatar
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from errors import ValidationError, NotFoundError, UnauthorizedError, ConflictError
from schemas import (
    UserRegisterSchema, UserLoginSchema, UserUpdateSchema, 
    ChangePasswordSchema, UserSchema, ForgotPasswordSchema,
    VerifyCodeSchema, ResetPasswordSchema
)
from datetime import datetime, timedelta
import random
import os

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """Регистрация нового пользователя"""
    try:
        schema = UserRegisterSchema()
        data = schema.load(request.form.to_dict())
        
        email = data.get("email")
        if User.query.filter_by(email=email).first():
            raise ConflictError("Пользователь с таким email уже существует")

        user = User(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=email
        )
        user.set_password(data["password"])

        if "avatar" in request.files:
            f = request.files["avatar"]
            if f.filename:
                saved = save_avatar(f)
                if saved is None:
                    raise ValidationError("Недопустимое расширение файла аватара")
                user.avatar = saved

        db.session.add(user)
        db.session.commit()
        
        user_schema = UserSchema()
        return jsonify({
            "success": True,
            "message": "Пользователь успешно создан",
            "user": user_schema.dump(user),
            "user_id": user.id
        }), 201
    except ValidationError as e:
        raise
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Ошибка при создании пользователя: {str(e)}")

@auth_bp.route("/login", methods=["POST"])
def login():
    """Вход в систему"""
    try:
        schema = UserLoginSchema()
        data = schema.load(request.get_json() or {})
        
        user = User.query.filter_by(email=data["email"]).first()
        if not user or not user.check_password(data["password"]):
            raise UnauthorizedError("Неверный email или пароль")
        
        access_token = create_access_token(identity=str(user.id))
        user_schema = UserSchema()
        
        return jsonify({
            "success": True,
            "access_token": access_token,
            "user": user_schema.dump(user)
        }), 200
    except ValidationError as e:
        raise
    except Exception as e:
        raise UnauthorizedError("Ошибка при входе в систему")

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Получить информацию о текущем пользователе"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError("Пользователь не найден")
    
    user_schema = UserSchema()
    return jsonify({
        "success": True,
        "user": user_schema.dump(user)
    }), 200

@auth_bp.route("/avatar/<filename>", methods=["GET"])
def avatar(filename):
    """Получить аватар пользователя"""
    folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(folder, filename)

@auth_bp.route("/update", methods=["PUT"])
@jwt_required()
def update_profile():
    """Обновить профиль пользователя"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        
        schema = UserUpdateSchema()
        data = schema.load(request.form.to_dict())
        
        if "first_name" in data:
            user.first_name = data["first_name"]
        if "last_name" in data:
            user.last_name = data["last_name"]
        if "email" in data:
            new_email = data["email"]
            existing = User.query.filter_by(email=new_email).first()
            if existing and existing.id != user.id:
                raise ConflictError("Email уже используется другим пользователем")
            user.email = new_email
        if "phone" in data:
            # Пока phone не в модели User, можно добавить позже
            # user.phone = data["phone"]
            pass
        
        if "avatar" in request.files:
            f = request.files["avatar"]
            if f.filename:
                saved = save_avatar(f)
                if saved is None:
                    raise ValidationError("Недопустимое расширение файла аватара")
                user.avatar = saved
        
        db.session.commit()
        user_schema = UserSchema()
        
        return jsonify({
            "success": True,
            "message": "Профиль успешно обновлен",
            "user": user_schema.dump(user)
        }), 200
    except (ValidationError, ConflictError) as e:
        raise
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Ошибка при обновлении профиля: {str(e)}")

@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """Изменить пароль"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        
        schema = ChangePasswordSchema()
        data = schema.load(request.get_json() or {})
        
        if not user.check_password(data["old_password"]):
            raise UnauthorizedError("Неверный текущий пароль")
        
        user.set_password(data["new_password"])
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Пароль успешно изменен"
        }), 200
    except (ValidationError, UnauthorizedError) as e:
        raise
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Ошибка при изменении пароля: {str(e)}")

def generate_reset_code():
    """Генерирует 6-значный код восстановления"""
    return str(random.randint(100000, 999999))

def send_reset_code_email(email, code):
    """
    Отправляет код восстановления на email
    В production здесь должна быть реальная отправка email
    """
    # TODO: Реализовать отправку email через SMTP или сервис (SendGrid, Mailgun и т.д.)
    # Для разработки просто логируем
    if current_app.config.get('FLASK_ENV') == 'development':
        print(f"[DEV] Код восстановления для {email}: {code}")
    # В production:
    # from flask_mail import Message
    # msg = Message('Код восстановления пароля', recipients=[email])
    # msg.body = f'Ваш код восстановления: {code}'
    # mail.send(msg)

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """Отправка кода восстановления пароля"""
    try:
        schema = ForgotPasswordSchema()
        data = schema.load(request.get_json() or {})
        email = data["email"]
        
        # Проверяем, существует ли пользователь
        user = User.query.filter_by(email=email).first()
        if not user:
            # Для безопасности не сообщаем, что пользователь не найден
            return jsonify({
                "success": True,
                "message": "Если пользователь с таким email существует, код отправлен на вашу электронную почту"
            }), 200
        
        # Генерируем код
        code = generate_reset_code()
        expires_at = datetime.utcnow() + timedelta(minutes=15)  # Код действителен 15 минут
        
        # Помечаем старые коды как использованные
        PasswordResetCode.query.filter_by(email=email, used=False).update({"used": True})
        
        # Создаем новый код
        reset_code = PasswordResetCode(
            email=email,
            code=code,
            expires_at=expires_at
        )
        db.session.add(reset_code)
        db.session.commit()
        
        # Отправляем код (в production - реальный email)
        send_reset_code_email(email, code)
        
        return jsonify({
            "success": True,
            "message": "Код отправлен на вашу электронную почту"
        }), 200
    except ValidationError as e:
        raise
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Ошибка при отправке кода: {str(e)}")

@auth_bp.route("/verify-code", methods=["POST"])
def verify_code():
    """Проверка кода подтверждения"""
    try:
        schema = VerifyCodeSchema()
        data = schema.load(request.get_json() or {})
        email = data["email"]
        code = data["code"]
        
        # Ищем активный код
        reset_code = PasswordResetCode.query.filter_by(
            email=email,
            code=code,
            used=False
        ).filter(PasswordResetCode.expires_at > datetime.utcnow()).first()
        
        if not reset_code:
            raise UnauthorizedError("Неверный или истекший код")
        
        # Создаем временный токен для сброса пароля (действителен 10 минут)
        temp_token = create_access_token(
            identity=email,
            expires_delta=timedelta(minutes=10),
            additional_claims={"reset_password": True}
        )
        
        return jsonify({
            "success": True,
            "token": temp_token,
            "message": "Код подтвержден"
        }), 200
    except (ValidationError, UnauthorizedError) as e:
        raise
    except Exception as e:
        raise ValidationError(f"Ошибка при проверке кода: {str(e)}")

@auth_bp.route("/resend-code", methods=["POST"])
def resend_code():
    """Повторная отправка кода восстановления"""
    try:
        schema = ForgotPasswordSchema()
        data = schema.load(request.get_json() or {})
        email = data["email"]
        
        # Проверяем, существует ли пользователь
        user = User.query.filter_by(email=email).first()
        if not user:
            # Для безопасности не сообщаем, что пользователь не найден
            return jsonify({
                "success": True,
                "message": "Если пользователь с таким email существует, код отправлен повторно"
            }), 200
        
        # Генерируем новый код
        code = generate_reset_code()
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        # Помечаем старые коды как использованные
        PasswordResetCode.query.filter_by(email=email, used=False).update({"used": True})
        
        # Создаем новый код
        reset_code = PasswordResetCode(
            email=email,
            code=code,
            expires_at=expires_at
        )
        db.session.add(reset_code)
        db.session.commit()
        
        # Отправляем код
        send_reset_code_email(email, code)
        
        return jsonify({
            "success": True,
            "message": "Код отправлен повторно"
        }), 200
    except ValidationError as e:
        raise
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Ошибка при повторной отправке кода: {str(e)}")

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """Сброс пароля по коду"""
    try:
        schema = ResetPasswordSchema()
        data = schema.load(request.get_json() or {})
        email = data["email"]
        code = data["code"]
        new_password = data["new_password"]
        
        # Проверяем код
        reset_code = PasswordResetCode.query.filter_by(
            email=email,
            code=code,
            used=False
        ).filter(PasswordResetCode.expires_at > datetime.utcnow()).first()
        
        if not reset_code:
            raise UnauthorizedError("Неверный или истекший код")
        
        # Находим пользователя
        user = User.query.filter_by(email=email).first()
        if not user:
            raise NotFoundError("Пользователь не найден")
        
        # Устанавливаем новый пароль
        user.set_password(new_password)
        
        # Помечаем код как использованный
        reset_code.used = True
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Пароль успешно изменен"
        }), 200
    except (ValidationError, UnauthorizedError, NotFoundError) as e:
        raise
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Ошибка при сбросе пароля: {str(e)}")

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Выход из системы"""
    # В JWT токены stateless, поэтому просто возвращаем успех
    # В production можно добавить blacklist токенов
    return jsonify({
        "success": True,
        "message": "Вы успешно вышли из системы"
    }), 200


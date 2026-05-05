# app/services/auth_service.py

import jwt
from datetime import datetime, timedelta
from app.models.user import User
from app.config import Config


def register_user(user_code):
    # Verificar si ya existe
    existing = User.find_by_code(user_code)
    if existing:
        raise ValueError("El usuario ya existe")

    user = User(code=user_code)
    user.save()

    return user


def login_user(user_code):
    user = User.find_by_code(user_code)

    if not user:
        raise ValueError("Usuario no encontrado")

    token = generate_token(user)

    return token


def generate_token(user):
    payload = {
        "user_id": user.id,
        "code": user.code,
        "exp": datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    }

    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

    return token


def decode_token(token):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expirado")
    except jwt.InvalidTokenError:
        raise ValueError("Token inválido")

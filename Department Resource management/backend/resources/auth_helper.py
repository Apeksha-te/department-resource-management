import jwt
import datetime
from django.conf import settings
from django.contrib.auth.models import User

JWT_SECRET = getattr(settings, 'SECRET_KEY', 'jwt-super-secret-key-mce')
JWT_ALGORITHM = 'HS256'

def generate_token_for_user(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_user_from_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')
        return User.objects.filter(id=user_id).first()
    except Exception:
        return None

def get_authenticated_user(request):
    # Check Bearer token first
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        user = get_user_from_token(token)
        if user:
            return user
    # Fallback to session user
    if request.user and request.user.is_authenticated:
        return request.user
    return None

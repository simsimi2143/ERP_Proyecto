from functools import wraps
from flask import abort, current_app
from flask_login import current_user

def permission_required(module, level=1):
    """Decorador para verificar permisos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            
            if not current_user.has_permission(module, level):
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def superuser_required(f):
    """Decorador para requerir superusuario"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_superuser:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
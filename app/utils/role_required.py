from functools import wraps
from flask import render_template
from flask_login import login_required, current_user

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                return render_template("403.html", role=current_user.role.value), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

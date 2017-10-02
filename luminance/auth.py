from urllib.parse import urlparse, urljoin
from flask import request, url_for, redirect, flash
from flask_login import LoginManager, current_user
from functools import wraps
from .models import UserLevel

login_manager = LoginManager()


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if current_user.level not in (UserLevel.admin, UserLevel.root):
            flash('Insufficient priviliges.')
            print(current_user.level)
            return redirect(url_for('pages.index'))
        return f(*args, **kwargs)
    return decorator

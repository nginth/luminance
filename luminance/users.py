from flask import (
    current_app,
    Blueprint,
    render_template
)
from flask_login import current_user, login_required
from .database import db_session
from .models import User
from .auth import login_manager, admin_required

users = Blueprint('users', __name__, template_folder='templates/users')

@users.route('/')
@login_required
@admin_required
def admin_panel():
    users = User.query.all()
    return render_template('users/users_admin.html', users=users)

@users.route('/<string:username>')
def profile_page(username):
    print(username)
    user = User.query.filter(User.username == username).first()
    print(user)
    return render_template('users/profile.html', user=user)
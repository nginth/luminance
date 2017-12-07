from flask import (
    current_app,
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for
)
from flask_login import current_user, login_required
from .database import db_session
from .models import User
from .auth import login_manager, admin_required
from .forms import ProfileForm

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


@users.route('/<string:username>/edit', methods=['GET', 'POST'])
def edit_profile(username):
    user = User.query.filter(User.username == username).first()
    if not user.id == current_user.id and not current_user.is_admin:
        flash('Insufficient priviliges.')
        return redirect(url_for('users.profile_page', username=username))

    form = ProfileForm(request.form)
    if request.method == 'POST' and form.validate():
        user.description = form.bio.data
        db_session.add(user)
        db_session.commit()
        flash('Profile saved.')
        return redirect(url_for('users.edit_profile', username=user.username))

    return render_template('users/edit_profile.html', user=user, form=form)

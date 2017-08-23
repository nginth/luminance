from flask import (
    Flask, 
    render_template, 
    request, 
    flash, 
    redirect, 
    url_for,
    current_app,
    Blueprint
)
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from .forms import RegistrationForm, LoginForm, ContestForm, AddUserToEventForm
from .database import db_session
from .models import User, Event, UserLevel
from .auth import is_safe_url, login_manager, admin_required
from .flickr import flickrAPIUser, get_photo_urls

# TODO: actually make modular like this is intended to lol
pages = Blueprint('pages', __name__, template_folder='templates')

@pages.route('/')
def index(): 
    return render_template('index.html')

@pages.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    
    if request.method == 'POST' and form.validate():
        user = User.query.filter(User.username == form.username.data).first()
        if user and user.authenticate(form.password.data):
            login_user(user)
            flash('You have been logged in successfully.')
            next = request.args.get('next')
            if not is_safe_url(next):
                return flask.abort(400)
            return redirect(next or url_for('pages.index'))
        else:
            flash('Error logging in.')
            return redirect(url_for('pages.login'))    
    elif request.method == 'POST':
        flash('Error logging in.')
        return redirect(url_for('pages.login'))

    return render_template('login.html', form=form)

@pages.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('pages.index'))

@pages.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm(request.form)
    print(request.form)
    if request.method == 'POST' and form.validate():
        user = User(username=form.username.data, password=form.password.data)
        db_session.add(user)
        db_session.commit()
        flash('Thanks for registering!!')
        return redirect(url_for('pages.login'))

    return render_template('signup.html', form=form)

@pages.route('/contest', methods=['GET', 'POST'])
@login_required
@admin_required
def contest():
    form = ContestForm(request.form)
    if request.method == 'POST' and form.validate():
        contest = Event(name=form.name.data)
        contest.type = 'contest'
        print(form.start_date.data)
        print(form.end_date.data)
        if form.start_date.data:
            contest.start_date = form.start_date.data
        if form.end_date.data:
            contest.end_date = form.end_date.data
        contest.users.append(current_user)
        db_session.add(contest)
        db_session.commit()
        flash('Contest created.')
        return redirect(url_for('pages.contest'))

    return render_template('create_contest.html', form=form)

@pages.route('/admin')
@login_required
@admin_required
def admin_panel():
    return render_template('admin_panel.html')

@pages.route('/photos/test')
@login_required
def flickr_test():
    flickr = flickrAPIUser(current_user.username)
    flickr.authenticate_via_browser(perms='read')
    token = flickr.token_cache.token
    photos = flickr.photos.getPopular(user_id=token.user_nsid)['photos']['photo']
    photo_urls = get_photo_urls(photos)
    return render_template('photos.html', photo_urls=photo_urls)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id).first()

@login_manager.unauthorized_handler
def unauthorized():
    flash("You have to be logged in to access this page.")
    return redirect(url_for('pages.login', next=request.endpoint))

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
from .models import User, Event
from .auth import is_safe_url, login_manager
from .flickr import flickr

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

@pages.route('/events', methods=['GET', 'POST'])
def events():
    form = AddUserToEventForm(request.form)
    if request.method == 'POST' and form.validate():
        if current_user.is_anonymous or not current_user.is_authenticated:
            flash('You must log in to register for events.')
            return redirect(url_for('pages.events'))
        
        event = Event.query.filter(Event.id == form.event_id.data).first()
        if current_user in event.users:
            flash('You are already registered for this event!')
            return redirect(url_for('pages.events'))
        else: 
            event.users.append(current_user)
            db_session.add(event)
            db_session.commit()
            flash('Registration successful!')
            return redirect(url_for('pages.events'))
    else:
        events = Event.query.limit(10)
        return render_template('events.html', events=events, form=form)

@pages.route('/events/<int:event_id>')
def event_detail(event_id):
    event = Event.query.filter(Event.id == event_id).first()
    return render_template('event_detail.html', event=event)

# @pages.route('/photos/test')
# def flickr_test():
#     photos = flickr.photos.getPopular()
#     return render_template('photos.html', photos=photos)

@pages.route('/secret')
@login_required
def secret():
    return 'hi ' + current_user.username

@pages.route('/users/<string:username>')
def profile_page(username):
    print(username)
    user = User.query.filter(User.username == username).first()
    print(user)
    return render_template('profile.html', user=user)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id).first()

@login_manager.unauthorized_handler
def unauthorized():
    flash("You have to be logged in to access this page.")
    return redirect(url_for('pages.login', next=request.endpoint))
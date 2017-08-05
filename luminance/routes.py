from flask import (
    Flask, 
    render_template, 
    request, 
    flash, 
    redirect, 
    url_for
)
from luminance.luminance import app, login_manager
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from .forms import RegistrationForm, LoginForm, ContestForm, AddUserToEventForm
from .database import db_session
from .models import User, Event
from .auth import is_safe_url

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
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
            return redirect(next or url_for('index'))
        else:
            flash('Error logging in.')
            return redirect(url_for('login'))    
    elif request.method == 'POST':
        flash('Error logging in.')
        return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm(request.form)
    print(request.form)
    if request.method == 'POST' and form.validate():
        user = User(username=form.username.data, password=form.password.data)
        db_session.add(user)
        db_session.commit()
        flash('Thanks for registering!!')
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/contest', methods=['GET', 'POST'])
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
        return redirect(url_for('contest'))

    return render_template('create_contest.html', form=form)

@app.route('/events', methods=['GET', 'POST'])
def events():
    form = AddUserToEventForm(request.form)
    if request.method == 'POST' and form.validate():
        if current_user.is_anonymous or not current_user.is_authenticated:
            flash('You must log in to register for events.')
            return redirect(url_for('events'))
        
        event = Event.query.filter(Event.id == form.event_id.data).first()
        if current_user in event.users:
            flash('You are already registered for this event!')
            return redirect(url_for('events'))
        else: 
            event.users.append(current_user)
            db_session.add(event)
            db_session.commit()
            flash('Registration successful!')
            return redirect(url_for('events'))
    else:
        events = Event.query.limit(10)
        return render_template('events.html', events=events, form=form)

@app.route('/secret')
@login_required
def secret():
    return 'hi ' + current_user.username

@app.route('/users/<string:username>')
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
    return redirect(url_for('login', next=request.endpoint))

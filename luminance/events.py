from os import getcwd
from traceback import print_exc
from flask import (
    current_app,
    Blueprint,
    flash,
    url_for,
    request,
    redirect,
    render_template
)
from flask_login import current_user, login_required, login_manager
from werkzeug import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from .forms import AddUserToEventForm, PhotoForm, ChosenEventForm, ContestForm
from .database import db_session
from .models import Event, EventType, EventStatus, Photo, User
from .flickr import flickrAPIUser
from .auth import admin_required

events = Blueprint('events', __name__, template_folder='templates/events')


@events.route('/', methods=['GET', 'POST'])
def event_list():
    form = AddUserToEventForm(request.form)
    if request.method == 'POST' and form.validate():
        if current_user.is_anonymous or not current_user.is_authenticated:
            flash('You must log in to register for events.')
            return redirect(url_for('events.event_list'))

        event = Event.query.filter(Event.id == form.event_id.data).first()
        if current_user in event.users:
            flash('You are already registered for this event!')
            return redirect(url_for('events.event_list'))
        else:
            event.users.append(current_user)
            db_session.add(event)
            db_session.commit()
            flash('Registration successful!')
            return redirect(url_for('events.event_list'))
    else:
        events = Event.query.limit(10)
        return render_template('events.html', events=events, form=form)


@events.route('/<int:event_id>', methods=['GET', 'POST'])
def event_detail(event_id):
    event = Event.query.filter(Event.id == event_id).first()
    form = PhotoForm(CombinedMultiDict((request.files, request.form)))
    user_photo = next((p for p in event.photos if p.user_id ==
                       current_user.id), None) if not current_user.is_anonymous else None
    if request.method == 'POST':
        if user_photo != None:
            flash('You have already uploaded a photo to this event.')
            return redirect(url_for('events.event_detail', event_id=event.id))
        return event_upload(request, event, form)

    winner = Photo.query.filter(
        Photo.id == event.winner_id).first() if event.winner_id else None
    print(winner)
    return render_template('event_detail.html', event=event, form=form, photo=user_photo, winner=winner)


@events.route('/<int:event_id>/admin', methods=['GET', 'POST'])
def event_admin(event_id):
    event = Event.query.filter(Event.id == event_id).first()
    form = ChosenEventForm(request.form)

    if not current_user.id in event.admins:
        flash('Insufficient priviliges.')
        return redirect(url_for('events.event_detail', event_id=event_id))

    if request.method == 'POST' and form.validate():
        event.status = EventStatus.completed
        event.winner_id = form.photo_id.data
        user_id = Photo.query.filter(
            Photo.id == event.winner_id).first().user_id
        user = User.query.filter(User.id == user_id).first()
        user.exp += 100
        db_session.add(event)
        db_session.add(user)
        db_session.commit()
        flash('Winner chosen!')
        return redirect(url_for('events.event_detail', event_id=event_id))

    return render_template('event_admin.html', event=event, form=form)


@events.route('/<int:event_id>/edit', methods=['GET', 'POST'])
def event_edit(event_id):
    event = Event.query.filter(Event.id == event_id).first()
    form = ContestForm(request.form)

    if not current_user.id in event.admins:
        flash('Insufficient priviliges.')
        return redirect(url_for('events.event_detail', event_id=event_id))

    if request.method == 'POST' and form.validate():
        event.name = form.name.data
        event.start_date = form.start_date.data
        event.end_date = form.end_date.data
        db_session.add(event)
        db_session.commit()
        flash('Changes saved.')
        return redirect(url_for('events.event_detail', event_id=event_id))

    return render_template('event_edit.html', event=event, form=form)


@events.route('/contest', methods=['GET', 'POST'])
@login_required
@admin_required
def contest():
    form = ContestForm(request.form)
    if request.method == 'POST' and form.validate():
        contest = Event(name=form.name.data)
        contest.type = EventType.chosen
        if form.start_date.data:
            contest.start_date = form.start_date.data
        if form.end_date.data:
            contest.end_date = form.end_date.data
        if form.max_registrants.data:
            contest.max_registrants = form.max_registrants.data
        contest.users.append(current_user)
        contest.admins = [current_user.id]
        contest.status = EventStatus.inactive
        db_session.add(contest)
        db_session.commit()
        flash('Contest created.')
        return redirect(url_for('events.contest'))

    return render_template('create_contest.html', form=form)


def event_upload(request, event, form):
    if not form.validate():
        print('upload failed')
        flash('Upload failed.')
        return redirect(url_for('events.event_detail', event_id=event.id))
    if current_user.is_anonymous:
        print('user not logged in')
        flash('You must be logged in to do this.')
        return redirect(url_for('events.event_detail', event_id=event.id))
    if current_user not in event.users:
        flash('You must be registered for this event to do this.')
        return redirect(url_for('events.event_detail', event_id=event.id))

    photo = form.photo.data
    filename = secure_filename(form.photo.data.filename)
    filename = current_user.username + '_' + filename
    try:
        abs_filename = getcwd() + '/luminance/static/photos/' + filename
        form.photo.data.save(abs_filename)
        p = Photo(url='/static/photos/' + filename)
        current_user.photos.append(p)
        current_user.exp += 1
        event.photos.append(p)
        db_session.add(p)
        db_session.add(current_user)
        db_session.add(event)
        db_session.commit()
    except Exception:
        print_exc()
        flash('Upload failed.')
        return redirect(url_for('events.event_list'))

    flash('Upload successful!')
    return redirect(url_for('events.event_list'))


def flickr_upload(username, abs_filename, filename):
    flickr = flickrAPIUser(username)
    flickr.authenticate_via_browser(perms='write')

    with open(abs_filename) as f:
        try:
            resp = flickr.upload(
                title=filename,
                description='',
                tags='',
                fileobj=f,
                filename=filename,
                format='parsed-json'
            )
            flash('Upload successful!')
            print(resp)
            return True
        except Exception as e:
            print_exc()
            flash('Upload to flickr failed.')
            return False

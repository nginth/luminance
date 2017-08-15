from flask import (
    current_app, 
    Blueprint, 
    flash, 
    url_for, 
    request, 
    redirect,
    render_template
)
from flask_login import current_user
from werkzeug import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from .forms import AddUserToEventForm, PhotoForm
from .database import db_session
from .models import Event
from .flickr import flickrAPIUser

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
    if request.method == 'POST':
        return event_upload(request, event, form)

    return render_template('event_detail.html', event=event, form=form)

def event_upload(request, event, form):
    if not form.validate():
        print('upload failed')
        flash('Upload failed.')
        return redirect(url_for('events.event_detail', event_id=event.id))
    if current_user.is_anonymous:
        print('user not logged in')
        flash('You must be logged in to do this.')
        return redirect(url_for('events.event_detail', event_id=event.id))

    photo = form.photo.data
    filename = secure_filename(form.photo.data.filename)
    flickr = flickrAPIUser(current_user.username)
    flickr.authenticate_via_browser(perms='write')
    resp = flickr.upload(fileobj=photo, filename=filename)
    print(resp)
    flash('Upload successful!')
    return redirect(url_for('events.event_list'))

    
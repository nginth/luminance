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
from flask_login import current_user
from werkzeug import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from .forms import AddUserToEventForm, PhotoForm
from .database import db_session
from .models import Event, EventType, Photo
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
    user_photo = next((p for p in event.photos if p.user_id==current_user.id), None) if not current_user.is_anonymous else None
    if request.method == 'POST':
        if user_photo != None:
            flash('You have already uploaded a photo to this event.')
            return redirect(url_for('events.event_detail', event_id=event.id))
        return event_upload(request, event, form)

    return render_template('event_detail.html', event=event, form=form, photo=user_photo)

@events.route('/<int:event_id>/admin', methods=['GET', 'POST'])
def event_admin(event_id):
    event = Event.query.filter(Event.id == event_id).first()

    return render_template('event_admin.html', event=event)

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
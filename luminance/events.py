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
from .forms import AddUserToEventForm
from .database import db_session
from .models import Event

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

@events.route('/<int:event_id>')
def event_detail(event_id):
    event = Event.query.filter(Event.id == event_id).first()
    return render_template('event_detail.html', event=event)
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Boolean, 
    Table, 
    ForeignKey,
    DateTime
)
from sqlalchemy.orm import relationship
from luminance.database import Base
from werkzeug.security import generate_password_hash, check_password_hash

users_contests = Table('users_events', 
    Base.metadata,
    Column('user_id', Integer(), ForeignKey('users.id')),
    Column('event_id', Integer(), ForeignKey('events.id'))
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    session_key = Column(String(64), unique=True)
    pw_hash = Column(String(512))
    email = Column(String(120), unique=True)
    exp = Column(Integer)
    description = Column(String(20000))
    camera = Column(String(512))
    active = Column(Boolean)
    photos = relationship("Photo")

    @property
    def is_active(self):
        return self.active
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __init__(self, username=None, email=None, password=None):
        self.username = username
        self.email = email
        self.exp = 0
        self.set_password(password)
        self.active = True
    
    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def authenticate(self, password):
        return check_password_hash(self.pw_hash, password)
    
    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User {}, exp {}>'.format(self.username, self.exp)

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(String(1024), unique=True)
    users = relationship(
        "User",
        secondary=users_contests,
        backref="events"
    )
    type = Column(String(512))
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<Event<{}> {}>'.format(self.type, self.name)

class Photo(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True)
    url = Column(String(2048))
    user_id = Column(Integer, ForeignKey("users.id"))

    def __init__(self, url=None):
        self.url = url
    
    def __repr__(self):
        return '<Photo @ {}>'.format(self.url)
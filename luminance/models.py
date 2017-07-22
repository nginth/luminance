from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from luminance.database import Base
from werkzeug.security import generate_password_hash, check_password_hash

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    pw_hash = Column(String(512))
    email = Column(String(120), unique=True)
    exp = Column(Integer)
    description = Column(String(20000))
    camera = Column(String(512))
    active = Column(Boolean)

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

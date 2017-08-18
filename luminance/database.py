from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
engine = create_engine('postgresql://localhost/luminance', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import luminance.models
    Base.metadata.create_all(bind=engine)

def reset_db():
    engine.execute("drop schema public cascade;")
    engine.execute("create schema public;")
    init_db()
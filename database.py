from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func, String

# Replace 'sqlite:///rfg.db' with your path to database
engine = create_engine('mysql+pymysql://root:root@127.0.0.1:3306/flask_graphql', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	name = Column(Text)
	email = Column(Text)
	username = Column(String(255))

class Post(Base):
	__tablename__ = 'post'
	id = Column(Integer, primary_key=True)
	description = Column(Text)
	imageUrl = Column(Text)

class Message(Base):
	__tablename__ = 'message'
	id = Column(Integer, primary_key=True)
	message = Column(Text)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow)

class Sample(Base):
	__tablename__ = 'sample'
	id = Column(Integer, primary_key=True)
	message = Column(Text)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow)

# Include this if you want to autosync with DB
Base.metadata.create_all(bind=engine)
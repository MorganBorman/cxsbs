import sqlalchemy
from sqlalchemy.pool import NullPool

engine = sqlalchemy.create_engine("sqlite:///test.db", echo=False, poolclass=NullPool)

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ClanTag(Base):
	__tablename__ = "tags"
	id = Column(Integer, primary_key=True)
	tag = Column(String(16), index=True)
	group = Column(String(16), index=True)
	def __init__(self, tag, group):
		self.tag = tag
		self.group = group
		
Base.metadata.create_all(engine)

while True:
	session = sqlalchemy.orm.sessionmaker(bind=engine, autocommit=False, autoflush=True)()
	session.query(ClanTag).all()
	session.flush()
	session.expire_all()
	session.expunge_all()
	session.close()
	del session

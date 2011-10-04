import sqlalchemy
from sqlalchemy.pool import NullPool

engine = sqlalchemy.create_engine("sqlite:///test.db", echo=False, poolclass=NullPool)
#engine = sqlalchemy.create_engine("postgresql://cxsbs:blahorcas@localhost:5432/cxsbs", echo=False, poolclass=NullPool)

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tag(Base):
	__tablename__ = "tags"
	id = Column(Integer, primary_key=True)
	tag = Column(String(16), index=True)
	group = Column(String(16), index=True)
	def __init__(self, tag, group):
		self.tag = tag
		self.group = group
		
Base.metadata.create_all(engine)

create_memory_leak = True

sessionFactory = sqlalchemy.orm.sessionmaker(bind=engine, autocommit=False, autoflush=True)

while True:
	session = sessionFactory()
	
	if create_memory_leak:
		session.query(Tag).all()
		
	#I think all of these get called automatically by session.close() but I'm putting them in for good measure
	session.flush()
	session.expire_all()
	session.expunge_all()
	
	
	session.close()
	del session

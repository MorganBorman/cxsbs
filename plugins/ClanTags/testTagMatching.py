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
    
    session.query("id", "tag", "group").from_statement("SELECT id, tag, group FROM tags where name=:name").params(name='ed').all()
    
    session.close()
    del session
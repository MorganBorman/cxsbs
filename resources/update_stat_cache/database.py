import os.path, sys

PydepsPath = os.path.abspath("../../pydeps")
sys.path.append(PydepsPath)

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool, SingletonThreadPool, QueuePool
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import relation, mapper
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.expression import func

Base = declarative_base()

uri = "postgresql://cxsbs:ads9371@localhost:5432/cxsbs"
engine = create_engine(uri, echo=False, poolclass=QueuePool, pool_size=20, max_overflow=0)
sessionFactory = sqlalchemy.orm.sessionmaker(bind=engine, autocommit=False, autoflush=False)

tableSettings = {}

tableSettings['user_table'] = "usermanager_users"
tableSettings['damage_spent_event_table_name'] = "usermanager_damage_spent_events"
tableSettings['damage_dealt_event_table_name'] = "usermanager_damage_dealt_events"
tableSettings['frag_event_table_name'] = "usermanager_frag_events"
tableSettings['death_event_table_name']= "usermanager_death_events"
tableSettings['connections_table_name'] = "usermanager_connection_history"
tableSettings['rank_cache_table_name'] = "usermanager_rank_cache"

class User(Base):
	__tablename__ = tableSettings["user_table"]
	id = Column(Integer, primary_key=True)
	email = Column(String(64), nullable=False)
	publicKey = Column(String(49), index=True)
	serverId = Column(Integer, nullable=True)
	def __init__(self, email, publicKey):
		self.email = email
		self.publicKey = publicKey

NOTUSER = -1

class DamageSpentEvent(Base):
	"each Damage spent event with a timestamp for each user account"
	__table_args__ = {'extend_existing': True}
	__tablename__= tableSettings["damage_spent_event_table_name"]
	id = Column(Integer, primary_key=True)
	userId = Column(Integer, index=True)
	timestamp = Column(BigInteger, index=True)
	mode = Column(Integer, index=True)
	gun = Column(Integer)
	amount = Column(Integer)
	
	def __init__(self, userId, timestamp, mode, gun, amount):
		self.userId = userId
		self.timestamp = timestamp
		self.mode = mode
		self.gun = gun
		self.amount = amount

class DamageDealtEvent(Base):
	"each damage dealt event with a timestamp for each user account"
	__table_args__ = {'extend_existing': True}
	__tablename__= tableSettings["damage_dealt_event_table_name"]
	id = Column(Integer, primary_key=True)
	userId = Column(Integer, index=True)
	timestamp = Column(BigInteger, index=True)
	mode = Column(Integer, index=True)
	gun = Column(Integer)
	amount = Column(Integer)
	
	def __init__(self, userId, timestamp, mode, gun, amount):
		self.userId = userId
		self.timestamp = timestamp
		self.mode = mode
		self.gun = gun
		self.amount = amount
	
TEAMKILL = -2
		
class FragEvent(Base):
	"each frag event with a timestamp for each user account"
	__table_args__ = {'extend_existing': True}
	__tablename__= tableSettings["frag_event_table_name"]
	id = Column(Integer, primary_key=True)
	userId = Column(Integer, index=True)
	targetId = Column(Integer, index=True)
	timestamp = Column(BigInteger, index=True)
	mode = Column(Integer, index=True)
	
	def __init__(self, userId, targetId, timestamp, mode):
		self.userId = userId
		self.targetId = targetId
		self.timestamp = timestamp
		self.mode = mode
	
SUICIDE = -3

class DeathEvent(Base):
	"each death event with a timestamp for each user account"
	__table_args__ = {'extend_existing': True}
	__tablename__= tableSettings["death_event_table_name"]
	id = Column(Integer, primary_key=True)
	userId = Column(Integer, index=True)
	causeId = Column(Integer, index=True)
	timestamp = Column(BigInteger, index=True)
	mode = Column(Integer, index=True)
	
	def __init__(self, userId, causeId, timestamp, mode):
		self.userId = userId
		self.causeId = causeId
		self.timestamp = timestamp
		self.mode = mode
		
class UserConnection(Base):
	"each death event with a timestamp for each user account"
	__table_args__ = {'extend_existing': True}
	__tablename__= tableSettings["connections_table_name"]
	id = Column(Integer, primary_key=True)
	userId = Column(Integer, index=True)
	connect_timestamp = Column(BigInteger, index=True)
	disconnect_timestamp = Column(BigInteger, index=True)
	
	def __init__(self, userId, connect_timestamp, disconnect_timestamp):
		self.userId = userId
		self.connect_timestamp = connect_timestamp
		self.disconnect_timestamp = disconnect_timestamp
		
class UserStatCache(Base):
	"Caches an entry for the most recent day including the day number since epoch and the users ranking points at up to the end of that day."
	__table_args__ = {'extend_existing': True}
	__tablename__= tableSettings["rank_cache_table_name"]
	id = Column(Integer, primary_key=True)
	userId = Column(Integer, index=True)
	day = Column(BigInteger, index=True)
	rank_points = Column(BigInteger, index=True)
	
	def __init__(self, userId, day, rank_points):
		self.userId = userId
		self.day = day
		self.rank_points = rank_points
		
Base.metadata.create_all(engine)
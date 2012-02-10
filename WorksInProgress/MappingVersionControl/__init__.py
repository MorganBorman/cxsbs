import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, func, Float, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import relation, mapper
from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()

import cxsbs
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
Messages = cxsbs.getResource("Messages")
Players = cxsbs.getResource("Players")
DatabaseManager = cxsbs.getResource("DatabaseManager")
Commands = cxsbs.getResource("Commands")
Events = cxsbs.getResource("Events")
ServerCore = cxsbs.getResource("ServerCore")
	
pluginCategory = "MappingVersionControl"

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="repository_table", 
												displayName="Repository table", 
												default="mvc_repositories",
												doc="Table name for storing the repository definitions."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="groups_table", 
												displayName="Groups table", 
												default="mvc_groups",
												doc="Table name for storing the repository groups."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="commit_table", 
												displayName="Commit table", 
												default="mvc_commits",
												doc="Table name for storing the repository commits."
											))

tableSettings = SettingsManager.getAccessor(DatabaseManager.getDbSettingsCategory(), pluginCategory)
	
Base = declarative_base()

class Repository(Base):
	__tablename__= tableSettings["repository_table"]
	id = Column(Integer, primary_key=True)
	name = Column(String(64), nullable=False)
	description = Column(String(128), nullable=False)
	ownerEmail = Column(String(64), nullable=False)
	def __init__(self, name, description, ownerEmail):
		self.name = name
		self.description = description
		self.ownerEmail = ownerEmail
		
class Commit(Base):
	__tablename__= tableSettings["commit_table"]
	id = Column(Integer, primary_key=True)
	repositoryId = Column(Integer, ForeignKey(tableSettings["repository_table"] + '.id'), nullable=False)
	message = Column(String(128), nullable=False)
	version = Column(Integer, nullable=False)
	crc = Column(Integer, nullable=False)
	data = Column(LargeBinary)
	repository = relation(Repository, primaryjoin=repositoryId==Repository.id)
	def __init__(self, repositoryId, message, version, crc, data):
		self.repositoryId = repositoryId
		self.message = message
		self.crc = crc
		self.data = data
		
class CommitGroup(Base):
	__tablename__ = tableSettings["groups_table"]
	repositoryId = Column(Integer, ForeignKey(tableSettings["repository_table"] + '.id'))
	group = Column(String(16))
	repository = relation(Repository, primaryjoin=repositoryId==Repository.id)
	UniqueConstraint('repositoryId', 'group', name='uq_repository_id_group')
	__mapper_args__ = {'primary_key':[repositoryId, group]}
	def __init__(self, repositoryId, group):
		self.repositoryId = repositoryId
		self.group = group
	
Base.metadata.create_all(DatabaseManager.dbmanager.engine)
	
"""
resources
	repositories
	server-bench

send "Player has uploaded a map" message
Event:server_bench_changed

get the server-bench
/getmap

overwrite the server-bench with whatever your client has
/sendmap

store a versioned state of the server-bench in the given repository with the given commit message
#vcm commit <repository> <commit message>

copy a given repository to the server-bench
#vcm clone <repository> (version)

create a new repository of the given name.
#vcm create <repository> <description>

give control of a repository to another user
#vcm give <repository> <cn|email>

delete a given repository
#vcm delete <repository>

download a version from the specified repository directly
#vcm download <repository>(:version)

add a group that is permitted to commit to the specified repository
#vcm addgroup <repository> <group>

remove a group from those that are permitted to commit to the specified repository
#vcm delgroup <repository> <group>
"""

lastData = ""

@Commands.commandHandler('vcm')
def onVersionedControlledMapping(cn, args):
	'''
	@description Get the server to send the last sent map to you.
	@usage
	@allowGroups __all__
	@denyGroups
	@doc Get the server to send the last sent map to you.
	'''
	ServerCore.sendEditMap(cn, lastData)

@Events.eventHandler('player_uploaded_map')
def onUploadedMapData(cn, data):
	global lastData
	lastData = data
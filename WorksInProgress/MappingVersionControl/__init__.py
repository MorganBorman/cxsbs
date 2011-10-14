import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, func, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound

import cxsbs
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
Messages = cxsbs.getResource("Messages")
Players = cxsbs.getResource("Players")
DatabaseManager = cxsbs.getResource("DatabaseManager")
Commands = cxsbs.getResource("Commands")
	
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
	message = Column(String(128), nullable=False)
	version = Column(Integer, nullable=False)
	hash = Column(String(32), nullable=False)
	data = Column(LargeBinary())
		
	
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
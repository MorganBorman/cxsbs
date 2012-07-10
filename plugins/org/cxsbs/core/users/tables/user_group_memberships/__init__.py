import pyTensible, org

class user_group_memberships(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {}
        Resources = {'UserGroupMembership': UserGroupMembership}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.users.tables.user_group_memberships')
        
@org.cxsbs.core.settings.manager.Setting
def table_name():
    """
    @category db_tables
    @display_name UserGroupMembership table name
    @wbpolicy never
    @doc What should the table which stores user group memberships be called?
    """
    return "user_group_memberships"

from sqlalchemy import SmallInteger, Integer, BigInteger, String, Boolean
from sqlalchemy import DateTime
from sqlalchemy import Column, Sequence, ForeignKey

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper, relationship, backref
from sqlalchemy.schema import UniqueConstraint

from enum import enum

User = org.cxsbs.core.users.tables.users.User
UserGroup = org.cxsbs.core.users.tables.user_groups.UserGroup

class UserGroupMembership(org.cxsbs.core.database.manager.SchemaBase):
    __tablename__ = settings["table_name"]
    id = Column(Integer, Sequence(__tablename__+'_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    group_id = Column(Integer, ForeignKey(UserGroup.id), nullable=False)
    
    UniqueConstraint(user_id, group_id, name=__tablename__+'_uq_user_id_group_id')
    
    user = relationship('User', back_populates="group_memberships")
    group = relationship('UserGroup')
    
    def __init__(self, user_id, group_id):
        self.user_id = user_id
        self.name = group_id
import pyTensible, org

class users(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {}
        Resources = {'User': User}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.users.tables.users')
        
@org.cxsbs.core.settings.manager.Setting
def table_name():
    """
    @category db_tables
    @display_name User table name
    @wbpolicy never
    @doc What should the table which stores users be called?
    """
    return "users"

from sqlalchemy import SmallInteger, Integer, BigInteger, String, Boolean
from sqlalchemy import DateTime
from sqlalchemy import Column, Sequence, ForeignKey

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper, relationship, backref
from sqlalchemy.schema import UniqueConstraint

from enum import enum
    
class User(org.cxsbs.core.database.manager.SchemaBase):
    __tablename__ = settings["table_name"]
    id = Column(Integer, Sequence(__tablename__ + '_id_seq'), primary_key=True)
    email = Column(String(128), index=True)
    pubkey = Column(String(49), nullable=False)
    approved = Column(Boolean)
    
    UniqueConstraint(email, name=__tablename__+'_uq_email')
    
    names = relationship('UserName', order_by='UserName.id', back_populates="user")
    group_memberships = relationship('UserGroupMembership', order_by='UserGroupMembership.id', back_populates="user")
    
    def __init__(self, email, pubkey):
        self.email = email
        self.pubkey = pubkey
        self.approved = True
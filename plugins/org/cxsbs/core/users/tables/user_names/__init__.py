import pyTensible, org

class user_names(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {}
        Resources = {'UserName': UserName}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.users.tables.user_names')
        
@org.cxsbs.core.settings.manager.Setting
def table_name():
    """
    @category db_tables
    @display_name UserName table name
    @wbpolicy never
    @doc What should the table which stores users names be called?
    """
    return "user_names"

from sqlalchemy import SmallInteger, Integer, BigInteger, String, Boolean
from sqlalchemy import DateTime
from sqlalchemy import Column, Sequence, ForeignKey

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper, relationship, backref
from sqlalchemy.schema import UniqueConstraint

from enum import enum

User = org.cxsbs.core.users.tables.users.User
        
class UserName(org.cxsbs.core.database.manager.SchemaBase):
    __tablename__ = settings["table_name"]
    id = Column(Integer, Sequence(__tablename__ + '_id_seq'), primary_key=True)
    user_id = Column(BigInteger,        ForeignKey(User.id),      nullable=False)
    name    = Column(String(16), nullable=False)
    
    UniqueConstraint(name, name=__tablename__+'_uq_name')
    
    user = relationship('User', back_populates="names")
    
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
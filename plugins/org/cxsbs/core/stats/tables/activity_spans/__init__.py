import pyTensible, org

class activity_spans(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {}
        Resources = {'ActivitySpan': ActivitySpan}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.stats.tables.activity_spans')
        
@org.cxsbs.core.settings.manager.Setting
def table_name():
    """
    @category db_tables
    @display_name ActivitySpan table name
    @wbpolicy never
    @doc What should the table which stores user activity spans be called?
    """
    return "activity_spans"

from sqlalchemy import SmallInteger, Integer, BigInteger, String, Boolean
from sqlalchemy import DateTime
from sqlalchemy import Column, Sequence, ForeignKey

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper, relationship, backref
from sqlalchemy.schema import UniqueConstraint

from enum import enum

User = org.cxsbs.core.users.tables.users.User

class ActivitySpan(org.cxsbs.core.database.manager.SchemaBase):
    __tablename__ = settings["table_name"]
    id = Column(BigInteger, Sequence(__tablename__+'_id_seq'), primary_key=True)
    
    who     = Column(BigInteger,        ForeignKey(User.id),      nullable=False)
    
    type    = Column(SmallInteger,      nullable=False)
    start   = Column(DateTime,          nullable=False)
    end     = Column(DateTime,          nullable=False)
    millis  = Column(Integer,           nullable=False)

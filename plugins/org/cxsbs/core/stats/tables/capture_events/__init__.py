import pyTensible, org

class capture_events(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {}
        Resources = {'CaptureEvent': CaptureEvent}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.stats.tables.capture_events')
        
@org.cxsbs.core.settings.manager.Setting
def table_name():
    """
    @category db_tables
    @display_name CaptureEvent table name
    @wbpolicy never
    @doc What should the the table which stores capture events be called?
    """
    return "capture_events"

from sqlalchemy import SmallInteger, Integer, BigInteger, String, Boolean
from sqlalchemy import DateTime
from sqlalchemy import Column, Sequence, ForeignKey

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper, relationship, backref
from sqlalchemy.schema import UniqueConstraint

from enum import enum

User = org.cxsbs.core.users.tables.users.User
Match = org.cxsbs.core.stats.tables.matches.Match

class CaptureEvent(org.cxsbs.core.database.manager.SchemaBase):
    __tablename__ = settings["table_name"]
    id = Column(BigInteger, Sequence(__tablename__+'_id_seq'), primary_key=True)
    
    match_id    = Column(BigInteger,    ForeignKey(Match.id),    nullable=False)
    who_id      = Column(BigInteger,    ForeignKey(User.id),     nullable=False)
    
    start       = Column(DateTime,      nullable=False)
    end         = Column(DateTime,      nullable=False)
    team        = Column(SmallInteger,  nullable=True)
    complete    = Column(Boolean,       nullable=False)
    health      = Column(Integer,       nullable=False)

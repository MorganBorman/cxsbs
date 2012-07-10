import pyTensible, org

class frag_events(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {}
        Resources = {'FragEvent': FragEvent}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.stats.tables.frag_events')
        
@org.cxsbs.core.settings.manager.Setting
def table_name():
    """
    @category db_tables
    @display_name FragEvent table name
    @wbpolicy never
    @doc What should the table which stores frag events be called?
    """
    return "frag_events"

from sqlalchemy import SmallInteger, Integer, BigInteger, String, Boolean
from sqlalchemy import DateTime
from sqlalchemy import Column, Sequence, ForeignKey

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper, relationship, backref
from sqlalchemy.schema import UniqueConstraint

from enum import enum

User = org.cxsbs.core.users.tables.users.User
Match = org.cxsbs.core.stats.tables.matches.Match
ShotEvent = org.cxsbs.core.stats.tables.shot_events.ShotEvent

class FragEvent(org.cxsbs.core.database.manager.SchemaBase):
    __tablename__ = settings["table_name"]
    id = Column(BigInteger, Sequence(__tablename__+'_id_seq'), primary_key=True)
    
    who_id      = Column(BigInteger,    ForeignKey(User.id),         nullable=False)
    match_id    = Column(BigInteger,    ForeignKey(Match.id),       nullable=False)
    shot_id     = Column(BigInteger,    ForeignKey(ShotEvent.id),   nullable=False)
    target_id   = Column(BigInteger,    ForeignKey(User.id),         nullable=True)
    
    when        = Column(DateTime,      nullable=False)
    type        = Column(SmallInteger,  nullable=False)
    
    types = enum(NORMAL=0, TEAMKILL=1, BOT=2, SPAWNKILL=3)
    
    who = relationship('User', primaryjoin="User.id==FragEvent.who_id")
    match = relationship('Match')
    shot = relationship('ShotEvent')
    target = relationship('User', primaryjoin="User.id==FragEvent.target_id")
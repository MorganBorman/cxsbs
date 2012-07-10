import pyTensible, org

class death_events(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {}
        Resources = {'DeathEvent': DeathEvent}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.stats.tables.death_events')
        
@org.cxsbs.core.settings.manager.Setting
def table_name():
    """
    @category db_tables
    @display_name DeathEvent table name
    @wbpolicy never
    @doc What should the table which stores death events be called?
    """
    return "death_events"

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

class DeathEvent(org.cxsbs.core.database.manager.SchemaBase):
    __tablename__ = settings["table_name"]
    id = Column(BigInteger, Sequence(__tablename__+'_id_seq'), primary_key=True)
    
    who_id      = Column(BigInteger,    ForeignKey(User.id),         nullable=False)
    match_id    = Column(BigInteger,    ForeignKey(Match.id),       nullable=False)
    killer_id   = Column(BigInteger,    ForeignKey(User.id),         nullable=True)
    shot        = Column(BigInteger,    ForeignKey(ShotEvent.id),   nullable=True)
    
    when        = Column(DateTime,      nullable=False)
    type        = Column(SmallInteger,  nullable=False)


import pyTensible, org

class shot_events(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {}
        Resources = {'ShotEvent': ShotEvent}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.stats.tables.shot_events')
        
@org.cxsbs.core.settings.manager.Setting
def table_name():
    """
    @category db_tables
    @display_name ShotEvent table name
    @wbpolicy never
    @doc What should the table which stores shot events be called?
    """
    return "shot_events"

from sqlalchemy import SmallInteger, Integer, BigInteger, String, Boolean
from sqlalchemy import DateTime
from sqlalchemy import Column, Sequence, ForeignKey

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper, relationship, backref
from sqlalchemy.schema import UniqueConstraint

from enum import enum

User = org.cxsbs.core.users.tables.users.User
Match = org.cxsbs.core.stats.tables.matches.Match
Gun = org.cxsbs.core.common_tables.guns.Gun
ActivitySpan = org.cxsbs.core.stats.tables.activity_spans.ActivitySpan

class ShotEvent(org.cxsbs.core.database.manager.SchemaBase):
    __tablename__ = settings["table_name"]
    id          = Column(BigInteger, primary_key=True)
    
    id_generator = org.cxsbs.core.database.manager.HiLoIdGen(__tablename__)
    
    match_id            = Column(BigInteger,    ForeignKey(Match.id),           nullable=False)
    who_id              = Column(BigInteger,    ForeignKey(User.id),            nullable=False)
    gun_id              = Column(SmallInteger,  ForeignKey(Gun.id),             nullable=False)
    activity_span_id    = Column(BigInteger,    ForeignKey(ActivitySpan.id),    nullable=False)
    
    when        = Column(DateTime, nullable=False)
    
    match = relationship('Match')
    who = relationship('User')
    gun = relationship('Gun')
    activity_span = relationship('ActivitySpan')

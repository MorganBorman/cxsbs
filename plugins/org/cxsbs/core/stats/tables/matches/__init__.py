import pyTensible, org

class matches(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {}
        Resources = {'Match': Match}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.stats.tables.matches')
        
@org.cxsbs.core.settings.manager.Setting
def table_name():
    """
    @category db_tables
    @display_name Match table name
    @wbpolicy never
    @doc What should the table which stores matches be called?
    """
    return "matches"

from sqlalchemy import SmallInteger, Integer, BigInteger, String, Boolean
from sqlalchemy import DateTime
from sqlalchemy import Column, Sequence, ForeignKey

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper, relationship, backref
from sqlalchemy.schema import UniqueConstraint

from enum import enum

Mode = org.cxsbs.core.common_tables.modes.Mode
PseudoMode = org.cxsbs.core.common_tables.pseudomodes.PseudoMode
Instance = org.cxsbs.core.common_tables.instances.Instance

class Match(org.cxsbs.core.database.manager.SchemaBase):
    __tablename__ = settings["table_name"]
    id              = Column(BigInteger,        Sequence(__tablename__+'_id_seq'), primary_key=True)
    
    mode_id         = Column(SmallInteger,      ForeignKey(Mode.id),            nullable=False)
    pseudomode_id   = Column(SmallInteger,      ForeignKey(PseudoMode.id),      nullable=False)
    instance_id     = Column(Integer,           ForeignKey(Instance.id),        nullable=False)
    
    start           = Column(DateTime,          nullable=False)
    end             = Column(DateTime,          nullable=False)


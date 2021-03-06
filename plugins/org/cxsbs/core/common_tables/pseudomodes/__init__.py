import pyTensible, org

class pseudomodes(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {}
        Resources = {'PseudoMode': PseudoMode}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.common_tables.pseudomodes')
        
@org.cxsbs.core.settings.manager.Setting
def table_name():
    """
    @category db_tables
    @display_name PseudoMode table name
    @wbpolicy never
    @doc What should the table which contains the pseudomodes be called?
    """
    return "pseudomodes"

from sqlalchemy import SmallInteger, Integer, BigInteger, String, Boolean
from sqlalchemy import DateTime
from sqlalchemy import Column, Sequence, ForeignKey

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper, relationship, backref
from sqlalchemy.schema import UniqueConstraint

from enum import enum

class PseudoMode(org.cxsbs.core.database.manager.SchemaBase):
    __tablename__ = settings["table_name"]
    id = Column(Integer, Sequence(__tablename__+'_id_seq'), primary_key=True)
    
    name            = Column(String(32),    nullable=False)

import pyTensible, org

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper
from sqlalchemy.schema import UniqueConstraint

class maps(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {}
        Resources = {'Map': Map}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.maps.tables.maps')
        
@org.cxsbs.core.settings.manager.Setting
def map_table_name():
    """
    @category db_tables
    @display_name Maps table name
    @wbpolicy never
    @doc What should the table which stores the map name:crc associations be called?
    """
    return "maps"

class Map(org.cxsbs.core.database.manager.SchemaBase):
    '''Associates a map CRC with a map name as the required map CRC'''
    __tablename__ = settings["map_table_name"]
    id = Column(Integer, primary_key=True)
    mapName = Column(String(16), index=True)
    mapCrc = Column(Integer, index=True)
    def __init__(self, mapName, mapCrc):
        self.mapName = mapName
        self.mapCrc = mapCrc
        
    @staticmethod
    def update(map_name, crc):
        with org.cxsbs.core.database.manager.Session() as session:
            try:
                map_entry = session.query(Map).filter(Map.mapName==map_name).one()
                map_entry.mapCrc = crc
                session.add(map_entry)
                session.commit()
            except NoResultFound:
                map_entry = Map(map_name, crc)
                session.add(map_entry)
                session.commit()
                
    @staticmethod
    def retrieve(map_name):
        "Get the map entry for this map_name. Return None if it doesn't exist."
        with org.cxsbs.core.database.manager.Session() as session:
            try:
                return session.query(Map).filter(Map.mapName==map_name).one()
            except NoResultFound:
                return None
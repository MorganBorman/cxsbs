import pyTensible, org

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper
from sqlalchemy.schema import UniqueConstraint

class bases(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {}
        Resources = {'BaseList': BaseList}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.maps.tables.bases')
        
@org.cxsbs.core.settings.manager.Setting
def map_bases_table_name():
    """
    @category db_tables
    @display_name Map bases table name
    @wbpolicy never
    @doc What should the table which stores the map base lists be called?
    """
    return "map_bases"

Map = org.cxsbs.core.maps.tables.maps.Map

class BaseList(org.cxsbs.core.database.manager.SchemaBase):
    '''keeps an entry for each base in each mode that has an item list for each map.'''
    __tablename__ = settings["map_bases_table_name"]
    mapId = Column(Integer, ForeignKey(Map.id))
    mode = Column(Integer, index=True)
    id = Column(Integer, index=True)
    ammotype = Column(Integer)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)
    map = relation(Map, primaryjoin=mapId==Map.id)
    UniqueConstraint('mapId', 'mode', 'id', name='uq_mapid_mode_id')
    __mapper_args__ = {'primary_key':[mapId, mode, id]}
    def __init__(self, mapId, mode, id, ammotype, x, y, z):
        self.mapId = mapId
        self.mode = mode
        self.id = id
        self.ammotype = ammotype
        self.x = x
        self.y = y
        self.z = z
        
    @staticmethod
    def update(mapName, gameMode, base_list):
        map_entry = Map.retrieve(mapName)
        
        if map_entry == None:
            return
        
        with org.cxsbs.core.database.manager.manager.Session() as session:
            session.query(BaseList).filter(BaseList.mapId==map_entry.id).filter(BaseList.mode==gameMode).delete()
            session.commit()
            
            for id in range(len(base_list)):
                baseEntry = BaseList(map_entry.id, gameMode, id, base_list[id][0], base_list[id][1], base_list[id][2], base_list[id][3])
                session.add(baseEntry)
            session.commit()
            
    @staticmethod
    def retrieve(mapName, mode):
        map_entry = Map.retrieve(mapName)
        
        if map_entry == None:
            return
        
        with org.cxsbs.core.database.manager.manager.Session() as session:
            try:
                base_list = []
                
                base_results = session.query(BaseList).filter(BaseList.mapId==map_entry.id).filter(BaseList.mode==mode).order_by(BaseList.id.asc()).all()
                for base in base_results:
                    base_list.append((base.ammotype, base.x, base.y, base.z))
                    
                if len(base_list) == 0:
                    return None
                    
                return tuple(base_list)
            except NoResultFound:
                return None
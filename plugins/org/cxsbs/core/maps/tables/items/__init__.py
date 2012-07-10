import pyTensible, org

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper
from sqlalchemy.schema import UniqueConstraint

class items(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {}
        Resources = {'ItemList': ItemList}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.maps.tables.items')
        
@org.cxsbs.core.settings.manager.Setting
def map_items_table_name():
    """
    @category db_tables
    @display_name Map items table name
    @wbpolicy never
    @doc What should the table which stores the map item lists be called?
    """
    return "map_items"

Map = org.cxsbs.core.maps.tables.maps.Map

class ItemList(org.cxsbs.core.database.manager.SchemaBase):
    '''keeps an entry for each item in each mode that has an item list for each map.'''
    __tablename__ = settings["map_items_table_name"]
    mapId = Column(Integer, ForeignKey(Map.id))
    mode = Column(Integer, index=True)
    id = Column(Integer, index=True)
    type = Column(Integer)
    map = relation(Map, primaryjoin=mapId==Map.id)
    UniqueConstraint('mapId', 'mode', 'id', name='uq_mapid_mode_id')
    __mapper_args__ = {'primary_key':[mapId, mode, id]}
    def __init__(self, mapId, mode, id, type):
        self.mapId = mapId
        self.mode = mode
        self.id = id
        self.type = type
        
    @staticmethod
    def update(mapName, gameMode, item_list):
        map_entry = Map.retrieve(mapName)
        
        if map_entry == None:
            return
        
        with org.cxsbs.core.database.manager.Session() as session:
            session.query(ItemList).filter(ItemList.mapId==map_entry.id).filter(ItemList.mode==gameMode).delete()
            session.commit()
            
            for id in range(len(item_list)):
                itemEntry = ItemList(map_entry.id, gameMode, id, item_list[id])
                session.add(itemEntry)
            session.commit()
            
    @staticmethod
    def retrieve(mapName, mode):
        map_entry = Map.retrieve(mapName)
        
        if map_entry == None:
            return
        
        with org.cxsbs.core.database.manager.Session() as session:
            try:
                item_list = []
                
                item_results = session.query(ItemList).filter(ItemList.mapId==map_entry.id).filter(ItemList.mode==mode).order_by(ItemList.id.asc()).all()
                for item in item_results:
                    item_list.append(item.type)
                    
                if len(item_list) == 0:
                    return None
                    
                return tuple(item_list)
            except NoResultFound:
                return None
import pyTensible, org

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper
from sqlalchemy.schema import UniqueConstraint

class flags(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {}
        Resources = {'FlagList': FlagList}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.maps.tables.flags')
        
@org.cxsbs.core.settings.manager.Setting
def map_flags_table_name():
    """
    @category db_tables
    @display_name Map flags table name
    @wbpolicy never
    @doc What should the table which stores the map flag lists be called?
    """
    return "map_flags"

Map = org.cxsbs.core.maps.tables.maps.Map

class FlagList(org.cxsbs.core.database.manager.SchemaBase):
    '''keeps an entry for each flag in each mode that has an item list for each map.'''
    __tablename__ = settings["map_flags_table_name"]
    mapId = Column(Integer, ForeignKey(Map.id))
    mode = Column(Integer, index=True)
    id = Column(Integer, index=True)
    team = Column(Integer)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)
    map = relation(Map, primaryjoin=mapId==Map.id)
    UniqueConstraint('mapId', 'mode', 'id', name='uq_mapid_mode_id')
    __mapper_args__ = {'primary_key':[mapId, mode, id]}
    def __init__(self, mapId, mode, id, team, x, y, z):
        self.mapId = mapId
        self.mode = mode
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.z = z
        
    @staticmethod
    def update(mapName, gameMode, flag_list):
        map_entry = Map.retrieve(mapName)
        
        if map_entry == None:
            return
        
        with org.cxsbs.core.database.manager.Session() as session:
            session.query(FlagList).filter(FlagList.mapId==map_entry.id).filter(FlagList.mode==gameMode).delete()
            session.commit()
            
            for id in range(len(flag_list)):
                flagEntry = FlagList(map_entry.id, org.cxsbs.core.server.state.game_mode, id, flag_list[id][0], flag_list[id][1], flag_list[id][2], flag_list[id][3])
                session.add(flagEntry)
            session.commit()
        
    @staticmethod    
    def retrieve(mapName, mode):
        map_entry = Map.retrieve(mapName)
        
        if map_entry == None:
            return
        
        with org.cxsbs.core.database.manager.Session() as session:
            try:
                flag_list = []
                
                flag_results = session.query(FlagList).filter(FlagList.mapId==map_entry.id).filter(FlagList.mode==mode).order_by(FlagList.id.asc()).all()
                for flag in flag_results:
                    flag_list.append((flag.team, flag.x, flag.y, flag.z))
                    
                if len(flag_list) == 0:
                    return None
                    
                return tuple(flag_list)
            except NoResultFound:
                return None
import pyTensible, org 
import CategoryConfig, sqlalchemy
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy import SmallInteger, BigInteger, Column
from sqlalchemy.orm.exc import NoResultFound
from contextlib import contextmanager

class manager(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        self.database_manager = DatabaseManager()
            
        class PrefixTablesMeta(DeclarativeMeta):
            def __init__(cls, classname, bases, dict_):
                if '__tablename__' in dict_:
                    settings_manager = org.cxsbs.core.settings.manager.settings_manager
                    tables_prefix = settings_manager.get_setting('org.cxsbs.core.database.tables.prefix').value
                    cls.__tablename__ = dict_['__tablename__'] = tables_prefix + cls.__tablename__
                return DeclarativeMeta.__init__(cls, classname, bases, dict_)
        
        SchemaBase = declarative_base(metaclass=PrefixTablesMeta)
        
        org.cxsbs.core.database.interfaces.IDataSchema.register(SchemaBase)
        
        class HiLoIdTablesMeta(PrefixTablesMeta):
            def __init__(cls, classname, bases, dict_):
                if '__id_type__' in dict_:
                    cls.__id_type__ = dict_['__id_type__']
                else:
                    cls.__id_type__ = BigInteger
                    
                cls.id = Column(SmallInteger, primary_key=True)
                cls.value = Column(cls.__id_type__, nullable=False, default=0)
                
                return PrefixTablesMeta.__init__(cls, classname, bases, dict_)
            
            def fetch(cls, quantity=100):
                """returns a tuple indicating an inclusive range of ids which have been reserved.
                
                returns (first_id, last_id)
                """
                with org.cxsbs.core.database.manager.Session() as session:
                    #session.execute("LOCK TABLES %s WRITE" % cls.__tablename__)
                    
                    try:
                        try:
                            entry = session.query(cls).filter(cls.id==1).with_lockmode('update').one()
                        except NoResultFound:
                            entry = cls()
                            entry.id = 1
                            entry.value = 0
                            session.add(entry)
                        
                        start_hival = entry.value
                        entry.value += quantity
                        
                        return (start_hival, entry.value-1)
                    finally:
                        session.commit()
                        #session.execute("UNLOCK TABLES")

        HiLoIdTablesBase = declarative_base(metaclass=HiLoIdTablesMeta)
        
        org.cxsbs.core.database.interfaces.IDataSchema.register(HiLoIdTablesBase)
        
        def HiLoIdGen(table_id):
            table_id = table_id + "_hilo_id"
            return type(table_id, (HiLoIdTablesBase,), dict(__tablename__ = table_id))
        
        Interfaces = {}
        Resources =     {
                            'database_manager': self.database_manager, 
                            'Session': Session,
                            'SchemaBase': SchemaBase,
                            'HiLoIdTablesBase': HiLoIdTablesBase,
                            'HiLoIdGen': HiLoIdGen
                        }
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass

def get_database_uri():
    config_path = org.cxsbs.core.server.instance.root
    config_category = "database"
    config_extension = ".conf"
    
    config_object = CategoryConfig.CategoryConfig(config_path, config_category, config_extension)
    
    #place the database by default in the instances directory
    default_db_path = "sqlite:///%s/../cxsbs.db" % org.cxsbs.core.server.instance.root
    
    doc = 'Sqlalchemy uri string indicating the database connection parameters.'
    return config_object.getOption('org.cxsbs.core.database.uri', default_db_path, doc)


class DatabaseManager():
    def __init__(self):
        self.is_connected = False
        self.uri = get_database_uri()
        self.engine = None
        self.session_factory = None
        
    def connect(self):
        if not self.is_connected:
            self.engine = sqlalchemy.create_engine(self.uri)
            self.session_factory = sqlalchemy.orm.sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
            self.is_connected = True
    
    def get_session(self):
        try:
            self.engine.execute("SELECT 1;")
        except:
            del self.session_factory
            del self.engine
            self.is_connected = False
            self.connect()

        return self.session_factory()

@contextmanager
def Session():
    session = org.cxsbs.core.database.manager.database_manager.get_session()
    try:
        yield session
    finally:
        session.close()
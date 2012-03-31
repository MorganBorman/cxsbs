import pyTensible, org 
import CategoryConfig, sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

class database(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        self.database_manager = DatabaseManager()
        
        Interfaces = {}
        Resources =     {
                            'manager': self.database_manager, 
                            'Session': Session, 
                            'Base': self.database_manager.Base, 
                            'initialize_tables': self.database_manager.initialize_tables,
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
        self.Base = declarative_base()
        
    def connect(self):
        if not self.is_connected:
            self.engine = sqlalchemy.create_engine(self.uri)
            self.session_factory = sqlalchemy.orm.sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
            self.is_connected = True
            
    def initialize_tables(self):
        self.connect()
        self.Base.metadata.create_all(self.engine)
    
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
    session = org.cxsbs.core.database.manager.get_session()
    try:
        yield session
    finally:
        session.close()
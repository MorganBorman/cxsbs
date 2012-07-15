import pyTensible, org

class manager(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {}
        Resources = {}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
request_tables =    {
                     'matches_pks': org.cxsbs.core.stats.tables.matches.Match,
                     'activity_spans_pks': org.cxsbs.core.stats.tables.activity_spans.ActivitySpan,
                     'capture_events_pks': org.cxsbs.core.stats.tables.capture_events.CaptureEvent,
                     'damage_dealt_events_pks': org.cxsbs.core.stats.tables.damage_dealt_events.DamageDealtEvent,
                     'death_events_pks': org.cxsbs.core.stats.tables.death_events.DeathEvent,
                     'frag_events_pks': org.cxsbs.core.stats.tables.frag_events.FragEvent,
                     'shot_events_pks': org.cxsbs.core.stats.tables.shot_events.ShotEvent,
                     }

@org.cxsbs.core.data_requests.data_request_handler('matches_pks')
@org.cxsbs.core.data_requests.data_request_handler('activity_spans_pks')
@org.cxsbs.core.data_requests.data_request_handler('capture_events_pks')
@org.cxsbs.core.data_requests.data_request_handler('damage_dealt_events_pks')
@org.cxsbs.core.data_requests.data_request_handler('death_events_pks')
@org.cxsbs.core.data_requests.data_request_handler('frag_events_pks')
@org.cxsbs.core.data_requests.data_request_handler('shot_events_pks')
def on_request_pks(request):
    """
    @thread stats
    """
    
    Table = request_tables[request.name]
    
    callback = request.args[0]
    index = request.args[1]
    num_pks = request.args[2]
    
    cur, end = Table.id_generator.fetch(num_pks)
    
    callback(index, cur, end)


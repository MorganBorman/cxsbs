"""
All messages contain the 'type' field which indicates the message type.
{type: ...

When we connect to a server, the first message we expect to get back is the server's name as follows:
{type: 'server-name', name: '[FD] Mars'}

The server may at any point after this message send any of the following messages:
{type: 'server-error', description: 'The specified ban id does not exist.', fatal: false}
{type: 'client-error', cn: 350, description: 'Insufficient permissions.', fatal: false}

{type: 'server-mm', mmode: 3, mmask: 0}

{type: 'game-refresh', players: [{cn: 2, name: '[FD]Oblivion', ip: '74.123.73.110', team: 'spectator', frags: 37, deaths: 21, suicides: 1, teamkills: 1, accuracy: 0.379, scores: 4}, ...], time: 302, paused: false, map: 'reissen', mode: 'efficctf'}
{type: 'game-change', mode: 'instactf', map: 'forge'}
{type: 'game-pause', value: true}
{type: 'game-connect', cn: 3, name: '[FD]Chasm', ip: '74.123.73.122'}
{type: 'game-name', cn: 3, name: '[FD]Chasm'}
{type: 'game-time', value: 355}
{type: 'game-frag', cn: 3, tcn: 5}
{type: 'game-suicide', cn: 3}
{type: 'game-accuracy', cn: 3, value: .353}
{type: 'game-score', cn: 3}
{type: 'game-changeteam', cn: 3, team: 'good'}
{type: 'game-teamscore', team: 'good', value: 30}
{type: 'game-disconnect', cn: 3}

{type: 'credential-flags', cn: 350, flags: ['ip', 'punitive', 'manage', 'timechange', 'mapchange', 'names', 'register', 'approve']} 

{type: 'punitive-res', action: 'ban', [{bip: '74.123.73.122', tip: '232.173.22.18', 

We may send the following requests to the server at any time
{type: 'request-credential-flags', cn: 350}
{type: 'request-game-refresh', cn: 350}
{type: 'request-server-mm'}
{type: 'request-punitive-sea', cn: 350, action: 'ban', parameter: 'tip', value: '232.173%'}

We may send the following commands to the server at any time
{type: 'command-punitive-act', cn: 350, action: 'ban', tcn: 5, seconds: 3600, reason: 'Impersonator', mask: '255.255.255.0'}
{type: 'command-punitive-ins', cn: 350, action: 'ban', tip: '232.173.22.18', seconds: 3600, reason: 'Impersonator', mask: '255.255.255.255'}
{type: 'command-punitive-exp', cn: 350, action: 'ban', id: 3444}
{type: 'command-punitive-upd', cn: 350, action: 'ban', id: 3444, tip: '232. 173.22.18', seconds: 3899, reason: -1, mask: '255.255.255.0'}

"""

class Server(object):
    def __init__(self, sock):
        self.socket = socket
        self.buffer = ""
        
    def handle(self):
        pass
    
    def handle_datum(self, datum):
        pass
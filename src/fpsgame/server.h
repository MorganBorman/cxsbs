/*

 This portion of the header is a redistribution of code origininally in the sauerbraten source code.

 */

#ifndef SB_SERVER_H
#define SB_SERVER_H

#include "game.h"

#define parseint(s) strtol((s), NULL, 0)

static inline float parsefloat(const char *s)
{
    // not all platforms (windows) can parse hexadecimal integers via strtod
    char *end;
    double val = strtod(s, &end);
    return val || end==s || (*end!='x' && *end!='X') ? float(val) : float(parseint(s));
}

// command
extern hashtable<const char *, ident> *idents;

namespace server
{
    extern int nextexceeded, gamemillis;

    struct server_entity            // server side version of "entity" type
    {
        int type;
        int spawntime;
        char spawned;
    };
	
    static const int DEATHMILLIS = 300;
	
    struct clientinfo;
	
    struct gameevent
    {
        virtual ~gameevent() {}
		
        virtual bool flush(clientinfo *ci, int fmillis);
        virtual void process(clientinfo *ci) {}
		
        virtual bool keepable() const { return false; }
    };
	
    struct timedevent : gameevent
    {
        int millis;
		
        bool flush(clientinfo *ci, int fmillis);
    };
	
    struct hitinfo
    {
        int target;
        int lifesequence;
        int rays;
        float dist;
        vec dir;
    };
	
    struct shotevent : timedevent
    {
        int id, gun;
        vec from, to;
        vector<hitinfo> hits;
		
        void process(clientinfo *ci);
    };
	
    struct explodeevent : timedevent
    {
        int id, gun;
        vector<hitinfo> hits;
		
        bool keepable() const { return true; }
		
        void process(clientinfo *ci);
    };
	
    struct suicideevent : gameevent
    {
        void process(clientinfo *ci);
    };
	
    struct pickupevent : gameevent
    {
        int ent;
		
        void process(clientinfo *ci);
    };
	
    template <int N>
    struct projectilestate
    {
        int projs[N];
        int numprojs;
		
        projectilestate() : numprojs(0) {}
		
        void reset() { numprojs = 0; }
		
        void add(int val)
        {
            if(numprojs>=N) numprojs = 0;
            projs[numprojs++] = val;
        }
		
        bool remove(int val)
        {
            loopi(numprojs) if(projs[i]==val)
            {
                projs[i] = projs[--numprojs];
                return true;
            }
            return false;
        }
    };

    enum {SE_D_SPENT, SE_D_DEALT, SE_FRAG, SE_DEATH};
    enum {SE_NOTUSER = -1, SE_TEAMKILL = -2, SE_SUICIDE = -3};

    struct stat_event
    {
    	short int type;
    	long int timestamp;
    	int uid;
    	int mode;
    	union {
    		int gun;
    		int target;
    		int cause;
    	};
    	int amount;
    };

    struct weapon_stat
    {
    	int damage_spent, damage_dealt;
    	int kills;
    	int spree, maxspree;

        void reset()
        {
        	damage_spent = damage_dealt = 0;
        	kills = 0;
        	spree = maxspree = 0;
        }
    };
	
    struct gamestate : fpsstate
    {
        vec o;
        projectilestate<8> rockets, grenades;

        int state, editstate;
        int lastdeath, lastspawn, lastshot, lasttimeplayed, lifesequence;

        //vector of timestamped stat events
        vector<stat_event *> stat_events;

        //stats stuff
        weapon_stat weapon_stats[GUN_PISTOL+1];

        //last kill info
        int lastkill, lastkill_weapon;

        //time totals
        int timeplayed, timespectated;

        //totals for regular stats
        int frags, deaths, teamkills, suicides, spree, maxspree;

        //totals for accuracy and effectiveness
        int damage_spent, damage_dealt, damage_received;

        //totals for ctf modes
        int flags_scored, flags_dropped, flags_stopped, flags_returned;
		
        gamestate() : state(CS_DEAD), editstate(CS_DEAD) {}
		
        bool isalive(int gamemillis)
        {
            return state==CS_ALIVE || (state==CS_DEAD && gamemillis - lastdeath <= DEATHMILLIS);
        }
		
        bool waitexpired(int gamemillis)
        {
            return gamemillis - lastshot >= gunwait;
        }
		
        void reset()
        {
            if(state<CS_SPECTATOR) state = editstate = CS_DEAD;
            maxhealth = 100;
            rockets.reset();
            grenades.reset();

            stat_events.deletecontents();

            lastdeath = lastspawn = lastshot = lasttimeplayed = lifesequence = 0;

            //reset the stats stuff
            loopi(GUN_PISTOL+1)
            {
            	weapon_stats[i].reset();
            }
            lastkill = lastkill_weapon = 0;
            timeplayed = timespectated = 0;
            frags = deaths = teamkills = suicides = spree = maxspree = 0;
            damage_spent = damage_dealt = damage_received = 0;
            flags_scored = flags_dropped = flags_stopped = flags_returned = 0;

            respawn();
        }

        void weapon_kill(int gun, int who)
        {
            loopi(GUN_PISTOL+1)
            {
            	if(i != gun)
            	{
            		if(weapon_stats[i].spree > 0)
            		{
            			if(weapon_stats[i].spree > weapon_stats[i].maxspree)
            			{
            				weapon_stats[i].maxspree = weapon_stats[i].spree;
            			}
            			SbPy::triggerEventf("client_weapon_spree_ended", "iii", who, gun, weapon_stats[i].spree);
            		}
            		weapon_stats[i].spree = 0;
            	}
            	else
            	{
            		weapon_stats[i].spree++;
            		if(weapon_stats[i].spree > 1)
            		{
            			if(weapon_stats[i].spree > weapon_stats[i].maxspree)
            			{
            				weapon_stats[i].maxspree = weapon_stats[i].spree;
            			}
            			SbPy::triggerEventf("client_weapon_spree", "iii", who, gun, weapon_stats[i].spree);
            		}
            	}
            }
        }

        void reset_sprees(int who)
        {
        	if (spree > maxspree)
        	{
        		maxspree = spree;
        	}
        	weapon_kill(-1, who);
        	spree = 0;
        }
		
        void respawn()
        {
            fpsstate::respawn();
            o = vec(-1e10f, -1e10f, -1e10f);
            lastdeath = 0;
            lastspawn = -1;
            lastshot = 0;
            lastkill = 0;
        }
		
        void reassign()
        {
            respawn();
            rockets.reset();
            grenades.reset();
        }
    };

    struct clientinfo
    {
        int clientnum, ownernum, connectmillis, sessionid, overflow, disconnect_reason;
        int uid;
        string name, team, mapvote;
        int playermodel;
        int modevote;
        int privilege;
        int connectstage;
        bool connected, local, timesync, active;
        string connectpwd;
        int gameoffset, lastevent, pushed, exceeded;
        gamestate state;
        vector<gameevent *> events;
        vector<uchar> position, messages;
        int posoff, poslen, msgoff, msglen;
        vector<clientinfo *> bots;
        uint authreq;
        string authname;
        int ping, aireinit;
        string clientmap;
        int mapcrc;
        bool warned, gameclip;
        ENetPacket *clipboard;
        int lastclipboard, needclipboard;

        clientinfo() : clipboard(NULL) { reset(); }
        ~clientinfo() { events.deletecontents(); cleanclipboard(); }

        void addevent(gameevent *e)
        {
            if(state.state>=CS_SPECTATOR || events.length()>100) delete e;
            else events.add(e);
        }

        enum
        {
            PUSHMILLIS = 2500
        };

        int calcpushrange()
        {
            ENetPeer *peer = getclientpeer(ownernum);
            return PUSHMILLIS + (peer ? peer->roundTripTime + peer->roundTripTimeVariance : ENET_PEER_DEFAULT_ROUND_TRIP_TIME);
        }

        bool checkpushed(int millis, int range)
        {
            return millis >= pushed - range && millis <= pushed + range;
        }

        void scheduleexceeded()
        {
            if(state.state!=CS_ALIVE || !exceeded) return;
            int range = calcpushrange();
            if(!nextexceeded || exceeded + range < nextexceeded) nextexceeded = exceeded + range;
        }

        void setexceeded()
        {
            if(state.state==CS_ALIVE && !exceeded && !checkpushed(gamemillis, calcpushrange())) exceeded = gamemillis;
            scheduleexceeded(); 
        }
            
        void setpushed()
        {
            pushed = max(pushed, gamemillis);
            if(exceeded && checkpushed(exceeded, calcpushrange())) exceeded = 0;
        }
        
        bool checkexceeded()
        {
            return state.state==CS_ALIVE && exceeded && gamemillis > exceeded + calcpushrange();
        }

        void mapchange()
        {
            mapvote[0] = 0;
            state.reset();
            events.deletecontents();
            overflow = 0;
            timesync = false;
            lastevent = 0;
            exceeded = 0;
            pushed = 0;
            clientmap[0] = '\0';
            mapcrc = 0;
            warned = false;
            gameclip = false;
        }

        void reassign()
        {
            state.reassign();
            events.deletecontents();
            timesync = false;
            lastevent = 0;
        }

        void cleanclipboard(bool fullclean = true)
        {
            if(clipboard) { if(--clipboard->referenceCount <= 0) enet_packet_destroy(clipboard); clipboard = NULL; }
            if(fullclean) lastclipboard = 0;
        }

        void reset()
        {
            name[0] = team[0] = connectpwd[0] = 0;
            uid = 1;
            disconnect_reason = -1;
            connectstage = 0;
            playermodel = -1;
            privilege = PRIV_NONE;
            connected = local = false;
            authreq = 0;
            position.setsize(0);
            messages.setsize(0);
            ping = 0;
            aireinit = 0;
            needclipboard = 0;
            cleanclipboard();
            mapchange();
        }

        int geteventmillis(int servmillis, int clientmillis)
        {
            if(!timesync || (events.empty() && state.waitexpired(servmillis)))
            {
                timesync = true;
                gameoffset = servmillis - clientmillis;
                return servmillis;
            }
            else return gameoffset + clientmillis;
        }
    };

    struct worldstate
    {
        int uses;
        vector<uchar> positions, messages;
    };
	
    struct ban
    {
        int time;
        uint ip;
    };
	
    namespace aiman
    {
        extern void removeai(clientinfo *ci);
        extern void clearai();
        extern void checkai();
        extern bool reqadd(clientinfo *ci, int skill);
        extern bool reqdel(clientinfo *ci);
        extern int botbalance;
        extern int botlimit;
        extern void setbotlimit(int limit);
        extern void setbotbalance(bool balance);
        extern void changemap();
        extern void addclient(clientinfo *ci);
        extern void changeteam(clientinfo *ci);
    }

   #define MM_MODE 0xF
   #define MM_AUTOAPPROVE 0x1000
   #define MM_PRIVSERV (MM_MODE | MM_AUTOAPPROVE)
   #define MM_PUBSERV ((1<<MM_OPEN) | (1<<MM_VETO))
   #define MM_COOPSERV (MM_AUTOAPPROVE | MM_PUBSERV | (1<<MM_LOCKED))

}

/*

 This portion of the header is a modified version of the sauerbraten source code.

*/
void fatal(const char *s, ...);

namespace server
{
	struct demofile
	{
		string info;
		uchar *data;
		int len;
	};

	extern int gamelimit;
	extern int gamemillis;
	extern bool allowShooting;
	extern int nextexceeded;
	extern vector<clientinfo *> connects, clients, bots;
	extern int mastermode;
	extern int mastermask;
	extern char smapname[260];

	extern char *pythonRoot;
	extern char *serverinitfile;
	extern char *instanceRoot;

	extern int publicserver;
	extern char *adminpass;
	extern char *serverpass;
	extern int gamemode;
	extern bool gamepaused;
	extern bool allow_modevote;
	extern bool demonextmatch;
	extern int persistentdemos;
	extern int capacity;
	extern int interm;
	extern int persistentintermission;
	extern stream *demorecord;
	extern vector<demofile> demos;

	struct servmode
	{
		virtual ~servmode() {}

		virtual void entergame(clientinfo *ci) {}
		virtual void leavegame(clientinfo *ci, bool disconnecting = false) {}

		virtual void moved(clientinfo *ci, const vec &oldpos, bool oldclip, const vec &newpos, bool newclip) {}
		virtual bool canspawn(clientinfo *ci, bool connecting = false) { return true; }
		virtual void spawned(clientinfo *ci) {}
		virtual void died(clientinfo *victim, clientinfo *actor) {}
		virtual bool canchangeteam(clientinfo *ci, const char *oldteam, const char *newteam) { return true; }
		virtual void changeteam(clientinfo *ci, const char *oldteam, const char *newteam) {}
		virtual void initclient(clientinfo *ci, packetbuf &p, bool connecting) {}
		virtual void update() {}
		virtual void reset(bool empty) {}
		virtual void intermission() {  }
		virtual bool hidefrags() { return false; }
        virtual void setteamscore(const char *team, int score) {}
		virtual int getteamscore(const char *team) { return 0; }
		virtual void getteamscores(vector<teamscore> &scores) {}
		virtual bool extinfoteam(const char *team, ucharbuf &p) { return false; }
	};

	extern servmode *smode;
	extern void setServMapItems(PyObject *args);
	extern PyObject *setServMapFlags(PyObject *args);
	extern PyObject *setServMapBases(PyObject *args);

	extern bool is_item_mode();
	extern bool is_capture_mode();
	extern bool is_flag_mode();

	extern void checkdisconnects(bool last);
	extern void reinitclients();

	int numclients(int exclude=-1, bool nospec=true, bool noai=true, bool priv=false, bool visible=true);
	void sendservmsg(const char *s);
	clientinfo *getinfo(int n);
	void hashPassword(int cn, int sessionid, char *pass, char *dest, int len);
	void setprivilege(clientinfo *ci, int priv);
	void pausegame(bool);
	void setmap(const char *, int);
	void setmastermode(int);
	void challengeauth(clientinfo *ci, uint id, const char *domain, const char *val);
	bool setteam(clientinfo *, char *);
	void sendClientInitialization(clientinfo *, int state);
	bool pregame_setteam(clientinfo *, char *);
	bool spectate(clientinfo *, bool);
	void setinvisible(clientinfo *, bool);
	void setTimeLeft(int milliseconds);
	void resetpriv(clientinfo *ci);
	void sendmapreload();
	void senddemo(int cn, uchar *data);
	void setupdemorecord();
	void enddemorecord();
	void suicide(clientinfo *ci);
	int numchannels();
}

extern void server_sigint(int);
extern int serverport;
extern int totalmillis;
extern char *serverip;

#endif


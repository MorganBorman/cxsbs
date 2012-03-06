/*

 This is a modified version of the original Sauerbraten source code.
 
*/

#include "sbpy.h"
#include "servermodule.h"
#include "server.h"

#include <iostream>

#include <signal.h>

namespace game
{
	void parseoptions(vector<const char *> &args)
	{
		loopv(args)
			if(!server::serveroption(args[i]))
				conoutf(CON_ERROR, "unknown command-line option: %s", args[i]);
	}
}

extern ENetAddress masteraddress;

namespace server
{

	bool notgotitems = true;		// true when map has changed and waiting for clients to send item
	int gamemode = 0;
	int gamemillis = 0, gamelimit = 0, nextexceeded = 0;
	bool gamepaused = false;

	string smapname = "";
	int interm = 0;
	bool mapreload = false;
	enet_uint32 lastsend = 0;
	int mastermode = MM_OPEN, mastermask = MM_PRIVSERV;
	int currentmaster = -1;
	stream *mapdata = NULL;

	vector<clientinfo *> connects, clients, bots;
	vector<worldstate *> worldstates;
	bool reliablemessages = false;
	bool checkexecqueue = false;
	bool allow_modevote = false;

	bool demonextmatch = false;
	stream *demotmp = NULL, *demorecord = NULL, *demoplayback = NULL;
	int nextplayback = 0, demomillis = 0;


#define SERVMODE 1
#include "capture.h"
#include "ctf.h"

	captureservmode capturemode;
	ctfservmode ctfmode;
	servmode *smode = NULL;

	VAR(exthideips, 0, 1, 1);
	VAR(allowshooting, 0, 1, 1);
	VAR(privateediting, 0, 0, 1);
	VAR(persistentintermission, 0, 0, 1);
	VAR(persistentdemos, 0, 1, 1);
	VAR(intermissionlength, 0, 10000, 30000);
	SVAR(serverdesc, "");
	VAR(serverprivate, 0, 0, 1);
	VAR(capacity, 0, maxclients, maxclients);

	SVAR(pythonRoot, ".");
	SVAR(pluginPath, "plugins");
	SVAR(instanceRoot, "instances/dev");

	VAR(publicserver, 0, 0, 2);
	SVAR(servermotd, "");

	void *newclientinfo() { return new clientinfo; }
	void deleteclientinfo(void *ci) { delete (clientinfo *)ci; }

	clientinfo *getinfo(int n)
	{
		if(n < MAXCLIENTS) return (clientinfo *)getclientinfo(n);
		n -= MAXCLIENTS;
		return bots.inrange(n) ? bots[n] : NULL;
	}

	vector<server_entity> sents;
	vector<savedscore> scores;

	int msgsizelookup(int msg)
	{
		static int sizetable[NUMSV] = { -1 };
		if(sizetable[0] < 0)
		{
			memset(sizetable, -1, sizeof(sizetable));
			for(const int *p = msgsizes; *p >= 0; p += 2) sizetable[p[0]] = p[1];
		}
		return msg >= 0 && msg < NUMSV ? sizetable[msg] : -1;
	}

	const char *modename(int n, const char *unknown)
	{
		if(m_valid(n)) return gamemodes[n - STARTGAMEMODE].name;
		return unknown;
	}

	const char *mastermodename(int n, const char *unknown)
	{
		return (n>=MM_START && size_t(n-MM_START)<sizeof(mastermodenames)/sizeof(mastermodenames[0])) ? mastermodenames[n-MM_START] : unknown;
	}

	const char *privname(int type)
	{
		switch(type)
		{
			case PRIV_ADMIN: return "admin";
			case PRIV_MASTER: return "master";
			default: return "unknown";
		}
	}

	void sendservmsg(const char *s) { sendf(-1, 1, "ris", N_SERVMSG, s); }

	void resetitems()
	{
		sents.shrink(0);
		//cps.reset();
	}

	bool serveroption(const char *arg)
	{
		if(arg[0]=='-') switch(arg[1])
		{
			case 'r': setsvar("pythonRoot", &arg[2]); return true;
			case 'p': setsvar("pluginPath", &arg[2]); return true;
			case 'i': setsvar("instanceRoot", &arg[2]); return true;
		}
		return false;
	}

	bool serverinit()
	{
		smapname[0] = '\0';
		resetitems();

		// Initialize python modules
		if(!SbPy::init("cxsbs_server", pythonRoot, pluginPath, instanceRoot))
			return false;
		return true;
	}

	int numclients(int exclude, bool nospec, bool noai, bool priv, bool visible)
	{
		int n = 0;
		loopv(clients)
		{
			clientinfo *ci = clients[i];
			if (i != exclude)
			{
				if (ci->state.state != CS_INVISIBLE || !visible)
				{
					if (ci->state.state != CS_SPECTATOR || !nospec)
					{
						if (ci->state.aitype == AI_NONE || !noai)
						{
							n++;
						}

					}
				}
			}
		}
		return n;
	}

	bool duplicatename(clientinfo *ci, char *name)
	{
		if(!name) name = ci->name;
		loopv(clients) if(clients[i]!=ci && !strcmp(name, clients[i]->name)) return true;
		return false;
	}

	const char *colorname(clientinfo *ci, char *name = NULL)
	{
		if(!name) name = ci->name;
		if(name[0] && !duplicatename(ci, name) && ci->state.aitype == AI_NONE) return name;
		static string cname[3];
		static int cidx = 0;
		cidx = (cidx+1)%3;
		formatstring(cname[cidx])(ci->state.aitype == AI_NONE ? "%s \fs\f5(%d)\fr" : "%s \fs\f5[%d]\fr", name, ci->clientnum);
		return cname[cidx];
	}

	bool canspawnitem(int type) { return !m_noitems && (type>=I_SHELLS && type<=I_QUAD && (!m_noammo || type<I_SHELLS || type>I_CARTRIDGES)); }

	int spawntime(int type)
	{
		if(m_classicsp) return INT_MAX;
		int np = numclients(-1, true, false);
		np = np<3 ? 4 : (np>4 ? 2 : 3);		// spawn times are dependent on number of players
		int sec = 0;
		switch(type)
		{
			case I_SHELLS:
			case I_BULLETS:
			case I_ROCKETS:
			case I_ROUNDS:
			case I_GRENADES:
			case I_CARTRIDGES: sec = np*4; break;
			case I_HEALTH: sec = np*5; break;
			case I_GREENARMOUR:
			case I_YELLOWARMOUR: sec = 20+rnd(10); break;
			case I_BOOST:
			case I_QUAD: sec = 40+rnd(40); break;
		}
		return sec*1000;
	}

	bool delayspawn(int type)
	{
		switch(type)
		{
			case I_GREENARMOUR:
			case I_YELLOWARMOUR:
				return !m_classicsp;
			case I_BOOST:
			case I_QUAD:
				return true;
			default:
				return false;
		}
	}


	bool pickup(int i, int sender)		// server side item pickup, acknowledge first client that gets it
	{
		if((m_timed && gamemillis>=gamelimit) || !sents.inrange(i) || !sents[i].spawned) return false;
		clientinfo *ci = getinfo(sender);
		if(ci->state.state >= CS_SPECTATOR) return false;
		if(!ci || (!ci->local && !ci->state.canpickup(sents[i].type))) return false;
		sents[i].spawned = false;
		sents[i].spawntime = spawntime(sents[i].type);
		sendf(-1, 1, "ri3", N_ITEMACC, i, sender);
		ci->state.pickup(sents[i].type);
		return true;
	}

	void setServMapItems(PyObject *args)
	{
		int numitems = 0;
		PyObject *tuple;
		int item_type;
		PyArg_ParseTuple(args, "O", &tuple);

		numitems = PyTuple_Size(tuple);

		loopi(numitems)
		{
			item_type = PyInt_AsLong(PyTuple_GetItem(tuple,i));

			server_entity se = { item_type, 0, false };
			sents.add(se);

			if(item_type && canspawnitem(sents[i].type))
			{
				if(m_mp(gamemode) && delayspawn(sents[i].type))
				{
					sents[i].spawntime = spawntime(sents[i].type);
				}
				else
				{
					sents[i].spawned = true;
				}
			}
		}

		notgotitems = false;
	}

	bool is_item_mode()
	{
		return !m_noitems;
	}


	PyObject *setServMapFlags(PyObject *args)
	{
		if (!m_ctf)
		{
			PyErr_SetString(PyExc_StandardError, "Can only set map flags during flag modes.");
			return 0;
		}

		ctfmode.setServMapFlags(args);

		Py_INCREF(Py_None);
		return Py_None;
	}

	PyObject *setServMapBases(PyObject *args)
	{
		if (!m_capture)
		{
			PyErr_SetString(PyExc_StandardError, "Can only set map bases during capture modes.");
			return 0;
		}

		capturemode.setServMapBases(args);

		Py_INCREF(Py_None);
		return Py_None;
	}

	clientinfo *choosebestclient(float &bestrank)
	{
		clientinfo *best = NULL;
		bestrank = -1;
		loopv(clients)
		{
			clientinfo *ci = clients[i];
			if(ci->state.state == CS_INVISIBLE) continue;
			if(ci->state.timeplayed<0) continue;
			float rank = ci->state.state!=CS_SPECTATOR ? ci->state.effectiveness/max(ci->state.timeplayed, 1) : -1;
			if(!best || rank > bestrank) { best = ci; bestrank = rank; }
		}
		return best;
	}

	bool setteam(clientinfo *ci, char *team)
	{
		if(!ci || !strcmp(ci->team, team)) return false;
		if(smode && ci->state.state==CS_ALIVE) smode->changeteam(ci, ci->team, team);
		copystring(ci->team, team);
		aiman::changeteam(ci);
		if(ci->state.state != CS_INVISIBLE)
		{
			sendf(-1, 1, "riis", N_SETTEAM, ci->clientnum, ci->team);
		}
		return true;
	}

	void switchteam(clientinfo *ci, char *team, int sender)
	{
		if(ci && strcmp(ci->team, team))
		{
			if(m_teammode && smode && !smode->canchangeteam(ci, ci->team, team))
				sendf(sender, 1, "riis", N_SETTEAM, sender, ci->team);
			else
			{
				if(smode && ci->state.state==CS_ALIVE)
					smode->changeteam(ci, ci->team, team);
				copystring(ci->team, team);
				aiman::changeteam(ci);
				sendf(-1, 1, "riis", N_SETTEAM, sender, ci->team);
			}
		}
	}

	/* This is a special purpose function for setting teams pre-game
	  which wont be effected by the autoteam function. */
	bool pregame_setteam(clientinfo *ci, char *team)
	{
		if(!ci) return false;
		if(ci->state.state == CS_INVISIBLE) return false;
		ci->state.timeplayed = -1;
		if(!strcmp(ci->team, team)) return true;
		copystring(ci->team, team, MAXTEAMLEN+1);
		sendf(-1, 1, "riis", N_SETTEAM, ci->clientnum, team);
		return true;
	}

	void autoteam()
	{
		static const char *teamnames[2] = {"good", "evil"};
		vector<clientinfo *> team[2];
		float teamrank[2] = {0, 0};
		int remaining = clients.length();
		SbPy::triggerEventf("autoteam", "");
		// We arent going to set clients already assigned a team
		clientinfo *ci;
		loopv(clients)
		{
			ci = clients[i];
			if(ci->state.timeplayed<0)
				remaining--;
		}
		// Do autoteam
		for(int round = 0; remaining>=0; round++)
		{
			int first = round&1, second = (round+1)&1, selected = 0;
			while(teamrank[first] <= teamrank[second])
			{
				float rank;
				clientinfo *ci = choosebestclient(rank);
				if(!ci) break;
				if(smode && smode->hidefrags()) rank = 1;
				else if(selected && rank<=0) break;
				ci->state.timeplayed = -1;
				team[first].add(ci);
				if(rank>0) teamrank[first] += rank;
				selected++;
				if(rank<=0) break;
			}
			if(!selected) break;
			remaining -= selected;
		}
		loopi(sizeof(team)/sizeof(team[0]))
		{
			loopvj(team[i])
			{
				clientinfo *ci = team[i][j];
				if(!strcmp(ci->team, teamnames[i])) continue;
				copystring(ci->team, teamnames[i], MAXTEAMLEN+1);
				if(ci->state.state != CS_INVISIBLE)
				{
					sendf(-1, 1, "riisi", N_SETTEAM, ci->clientnum, teamnames[i], -1);
				}
			}
		}
	}

	struct teamrank
	{
		const char *name;
		float rank;
		int clients;

		teamrank(const char *name) : name(name), rank(0), clients(0) {}
	};

	const char *chooseworstteam(const char *suggest = NULL, clientinfo *exclude = NULL)
	{
		teamrank teamranks[2] = { teamrank("good"), teamrank("evil") };
		const int numteams = sizeof(teamranks)/sizeof(teamranks[0]);
		loopv(clients)
		{
			clientinfo *ci = clients[i];
			if(ci==exclude || ci->state.aitype!=AI_NONE || ci->state.state==CS_SPECTATOR || !ci->team[0]) continue;
			ci->state.timeplayed += lastmillis - ci->state.lasttimeplayed;
			ci->state.lasttimeplayed = lastmillis;

			loopj(numteams) if(!strcmp(ci->team, teamranks[j].name))
			{
				teamrank &ts = teamranks[j];
				ts.rank += ci->state.effectiveness/max(ci->state.timeplayed, 1);
				ts.clients++;
				break;
			}
		}
		teamrank *worst = &teamranks[numteams-1];
		loopi(numteams-1)
		{
			teamrank &ts = teamranks[i];
			if(smode && smode->hidefrags())
			{
				if(ts.clients < worst->clients || (ts.clients == worst->clients && ts.rank < worst->rank)) worst = &ts;
			}
			else if(ts.rank < worst->rank || (ts.rank == worst->rank && ts.clients < worst->clients)) worst = &ts;
		}
		return worst->name;
	}

	int welcomepacket(packetbuf &p, clientinfo *ci);
	void sendwelcome(clientinfo *ci);

	int initclientpacket(packetbuf &p, clientinfo *ci);
	void sendClientInitialization(clientinfo *ci);

/** Demo Recording **/
	void writedemo(int chan, void *data, int len)
	{
		if(!demorecord) return;
		int stamp[3] = { gamemillis, chan, len };
		lilswap(stamp, 3);
		demorecord->write(stamp, sizeof(stamp));
		demorecord->write(data, len);
	}

	void recordpacket(int chan, void *data, int len)
	{
		writedemo(chan, data, len);
	}

	void enddemorecord()
	{
		if(!demorecord) return;
		DELETEP(demorecord);
		if(!demotmp) return;
		int len = demotmp->size();

		uchar *data = new uchar[len];
		demotmp->seek(0, SEEK_SET);
		demotmp->read(data, len);
		DELETEP(demotmp);

		SbPy::triggerEventf("demo_recorded", "sip", smapname, gamemode, Py_BuildValue("s#", data, len));
	}

	void setupdemorecord()
	{
		if(!m_mp(gamemode) || m_edit) return;

		demotmp = opentempfile("demorecord", "w+b");
		if(!demotmp) return;

		stream *f = opengzfile(NULL, "wb", demotmp);
		if(!f) { DELETEP(demotmp); return; }

		SbPy::triggerEventf("recording_demo", "");

		demorecord = f;

		demoheader hdr;
		memcpy(hdr.magic, DEMO_MAGIC, sizeof(hdr.magic));
		hdr.version = DEMO_VERSION;
		hdr.protocol = PROTOCOL_VERSION;
		lilswap(&hdr.version, 2);
		demorecord->write(&hdr, sizeof(demoheader));

		packetbuf p(MAXTRANS, ENET_PACKET_FLAG_RELIABLE);
		welcomepacket(p, NULL);
		initclientpacket(p, NULL);
		writedemo(1, p.buf, p.len);
	}
	/*
	void listdemos(int cn)
	{
		packetbuf p(MAXTRANS, ENET_PACKET_FLAG_RELIABLE);
		putint(p, N_SENDDEMOLIST);
		putint(p, demos.length());
		loopv(demos) sendstring(demos[i].info, p);
		sendpacket(cn, 1, p.finalize());
	}

	void cleardemos(int n)
	{
		if(!n)
		{
			loopv(demos) delete[] demos[i].data;
			demos.shrink(0);
			sendservmsg("cleared all demos");
		}
		else if(demos.inrange(n-1))
		{
			delete[] demos[n-1].data;
			demos.remove(n-1);
			defformatstring(msg)("cleared demo %d", n);
			sendservmsg(msg);
		}
	}

	void senddemo(int cn, int num)
	{
		if(!num) num = demos.length();
		if(!demos.inrange(num-1)) return;
		demofile &d = demos[num-1];
		sendf(cn, 2, "rim", N_SENDDEMO, d.len, d.data);
	}
*/

	void enddemoplayback()
	{
		if(!demoplayback) return;
		DELETEP(demoplayback);

		loopv(clients) sendf(clients[i]->clientnum, 1, "ri3", N_DEMOPLAYBACK, 0, clients[i]->clientnum);

		sendservmsg("demo playback finished");

		loopv(clients) sendwelcome(clients[i]);
	}

	void setupdemoplayback()
	{
		if(demoplayback) return;
		demoheader hdr;
		string msg;
		msg[0] = '\0';
		defformatstring(file)("%s.dmo", smapname);
		demoplayback = opengzfile(file, "rb");
		if(!demoplayback) formatstring(msg)("could not read demo \"%s\"", file);
		else if(demoplayback->read(&hdr, sizeof(demoheader))!=sizeof(demoheader) || memcmp(hdr.magic, DEMO_MAGIC, sizeof(hdr.magic)))
			formatstring(msg)("\"%s\" is not a demo file", file);
		else
		{
			lilswap(&hdr.version, 2);
			if(hdr.version!=DEMO_VERSION) formatstring(msg)("demo \"%s\" requires an %s version of Cube 2: Sauerbraten", file, hdr.version<DEMO_VERSION ? "older" : "newer");
			else if(hdr.protocol!=PROTOCOL_VERSION) formatstring(msg)("demo \"%s\" requires an %s version of Cube 2: Sauerbraten", file, hdr.protocol<PROTOCOL_VERSION ? "older" : "newer");
		}
		if(msg[0])
		{
			DELETEP(demoplayback);
			sendservmsg(msg);
			return;
		}

		formatstring(msg)("playing demo \"%s\"", file);
		sendservmsg(msg);

		demomillis = 0;
		sendf(-1, 1, "ri3", N_DEMOPLAYBACK, 1, -1);

		if(demoplayback->read(&nextplayback, sizeof(nextplayback))!=sizeof(nextplayback))
		{
			enddemoplayback();
			return;
		}
		lilswap(&nextplayback, 1);
	}

	void readdemo()
	{
		if(!demoplayback || gamepaused) return;
		demomillis += curtime;
		while(demomillis>=nextplayback)
		{
			int chan, len;
			if(demoplayback->read(&chan, sizeof(chan))!=sizeof(chan) ||
			  demoplayback->read(&len, sizeof(len))!=sizeof(len))
			{
				enddemoplayback();
				return;
			}
			lilswap(&chan, 1);
			lilswap(&len, 1);
			ENetPacket *packet = enet_packet_create(NULL, len, 0);
			if(!packet || demoplayback->read(packet->data, len)!=len)
			{
				if(packet) enet_packet_destroy(packet);
				enddemoplayback();
				return;
			}
			sendpacket(-1, chan, packet);
			if(!packet->referenceCount) enet_packet_destroy(packet);
			if(demoplayback->read(&nextplayback, sizeof(nextplayback))!=sizeof(nextplayback))
			{
				enddemoplayback();
				return;
			}
			lilswap(&nextplayback, 1);
		}
	}

	void stopdemo()
	{
		if(m_demo) enddemoplayback();
		else enddemorecord();
	}

	void pausegame(bool val)
	{
		if(gamepaused==val) return;
		gamepaused = val;
		sendf(-1, 1, "rii", N_PAUSEGAME, gamepaused ? 1 : 0);
	}

	void hashpassword(int cn, int sessionid, const char *pwd, char *result, int maxlen)
	{
		char buf[2*sizeof(string)];
		formatstring(buf)("%d %d ", cn, sessionid);
		copystring(&buf[strlen(buf)], pwd);
		if(!hashstring(buf, result, maxlen)) *result = '\0';
	}

	bool checkpassword(clientinfo *ci, const char *wanted, const char *given)
	{
		string hash;
		hashpassword(ci->clientnum, ci->sessionid, wanted, hash, sizeof(hash));
		return !strcmp(hash, given);
	}

	void revokemaster(clientinfo *ci)
	{
		ci->privilege = PRIV_NONE;
		if(ci->state.state==CS_SPECTATOR && !ci->local) aiman::removeai(ci);
		if(ci->privilege == PRIV_MASTER)
			SbPy::triggerEventf("client_master_revoked", "i", ci->clientnum);
		else
			SbPy::triggerEventf("client_admin_revoked", "i", ci->clientnum);
		if(ci->state.state != CS_INVISIBLE)
		{
				sendf(-1, 1, "ri4", N_CURRENTMASTER, -1, 0, mastermode);
			}
	}

	void setcimaster(clientinfo *ci)
	{
		loopv(clients) if(ci!=clients[i] && clients[i]->privilege<=PRIV_MASTER) revokemaster(clients[i]);
		if(ci)
		{
			ci->privilege = PRIV_MASTER;
			currentmaster = ci->clientnum;
			SbPy::triggerEventf("client_claimed_master", "i", ci->clientnum);
		}
		else
		{
			currentmaster = -1;
		}
		if(ci->state.state != CS_INVISIBLE)
		{
				sendf(-1, 1, "ri4", N_CURRENTMASTER, currentmaster, currentmaster >= 0 ? ci->privilege : 0, mastermode);
		}
	}

	void setciadmin(clientinfo *ci)
	{
		string msg;
		loopv(clients) if(ci!=clients[i] && clients[i]->privilege<=PRIV_MASTER) revokemaster(clients[i]);
		ci->privilege = PRIV_ADMIN;
		currentmaster = ci->clientnum;
		SbPy::triggerEventf("client_claimed_admin", "i", ci->clientnum);
		if(ci->state.state != CS_INVISIBLE)
		{
			sendf(-1, 1, "ri4", N_CURRENTMASTER, currentmaster, currentmaster >= 0 ? ci->privilege : 0, mastermode);
		}
	}

	void resetpriv(clientinfo *ci)
	{
		if(!ci || !ci->privilege) return;
		if(ci->privilege == PRIV_MASTER)
			SbPy::triggerEventf("client_released_master", "i", ci->clientnum);
		else
			SbPy::triggerEventf("client_released_admin", "i", ci->clientnum);
		revokemaster(ci);
		currentmaster = -1;
	}

	void setprivilege(clientinfo *ci, int priv)
	{
		switch(priv)
		{
			case PRIV_MASTER:
				setcimaster(ci);
				break;

			case PRIV_ADMIN:
				setciadmin(ci);
				break;
			default:
				resetpriv(ci);
				return;
		}
	}

	savedscore &findscore(clientinfo *ci, bool insert)
	{
		uint ip = getclientip(ci->clientnum);
		if(!ip && !ci->local) return *(savedscore *)0;
		if(!insert)
		{
			loopv(clients)
			{
				clientinfo *oi = clients[i];
				if(oi->clientnum != ci->clientnum && getclientip(oi->clientnum) == ip && !strcmp(oi->name, ci->name))
				{
					oi->state.timeplayed += lastmillis - oi->state.lasttimeplayed;
					oi->state.lasttimeplayed = lastmillis;
					static savedscore curscore;
					curscore.save(oi->state);
					return curscore;
				}
			}
		}
		loopv(scores)
		{
			savedscore &sc = scores[i];
			if(sc.ip == ip && !strcmp(sc.name, ci->name)) return sc;
		}
		if(!insert) return *(savedscore *)0;
		savedscore &sc = scores.add();
		sc.ip = ip;
		copystring(sc.name, ci->name);
		return sc;
	}

	void savescore(clientinfo *ci)
	{
		savedscore &sc = findscore(ci, true);
		if(&sc) sc.save(ci->state);
	}

	int checktype(int type, clientinfo *ci)
	{
		if(ci && ci->local) return type;
		// only allow edit messages in coop-edit mode
		if(type>=N_EDITENT && type<=N_EDITVAR && !m_edit) return -1;
		// server only messages
		static const int servtypes[] = { N_SERVINFO, N_INITCLIENT, N_WELCOME, N_MAPRELOAD, N_SERVMSG, N_DAMAGE, N_HITPUSH, N_SHOTFX, N_EXPLODEFX, N_DIED, N_SPAWNSTATE, N_FORCEDEATH, N_ITEMACC, N_ITEMSPAWN, N_TIMEUP, N_CDIS, N_CURRENTMASTER, N_PONG, N_RESUME, N_BASESCORE, N_BASEINFO, N_BASEREGEN, N_ANNOUNCE, N_SENDDEMOLIST, N_SENDDEMO, N_DEMOPLAYBACK, N_SENDMAP, N_DROPFLAG, N_SCOREFLAG, N_RETURNFLAG, N_RESETFLAG, N_INVISFLAG, N_CLIENT, N_AUTHCHAL, N_INITAI };
		if(ci)
		{
			loopi(sizeof(servtypes)/sizeof(int)) if(type == servtypes[i]) return -1;
			if(type < N_EDITENT || type > N_EDITVAR || !m_edit)
			{
				if(type != N_POS && ++ci->overflow >= 200) return -2;
			}
		}
		return type;
	}

	void cleanworldstate(ENetPacket *packet)
	{
		loopv(worldstates)
		{
			worldstate *ws = worldstates[i];
			if(ws->positions.inbuf(packet->data) || ws->messages.inbuf(packet->data)) ws->uses--;
			else continue;
			if(!ws->uses)
			{
				delete ws;
				worldstates.remove(i);
			}
			break;
		}
	}

	void flushclientposition(clientinfo &ci)
	{
		if(ci.position.empty() || (!hasnonlocalclients() && !demorecord)) return;
		if(ci.state.state == CS_INVISIBLE) return;
		packetbuf p(ci.position.length(), 0);
		p.put(ci.position.getbuf(), ci.position.length());
		ci.position.setsize(0);
		sendpacket(-1, 0, p.finalize(), ci.ownernum);
	}

	void addclientstate(worldstate &ws, clientinfo &ci)
	{
		if(ci.position.empty()) ci.posoff = -1;
		else
		{
			ci.posoff = ws.positions.length();
			ws.positions.put(ci.position.getbuf(), ci.position.length());
			ci.poslen = ws.positions.length() - ci.posoff;
			ci.position.setsize(0);
		}
		if(ci.messages.empty()) ci.msgoff = -1;
		else
		{
			ci.msgoff = ws.messages.length();
			putint(ws.messages, N_CLIENT);
			putint(ws.messages, ci.clientnum);
			putuint(ws.messages, ci.messages.length());
			ws.messages.put(ci.messages.getbuf(), ci.messages.length());
			ci.msglen = ws.messages.length() - ci.msgoff;
			ci.messages.setsize(0);
		}
	}

	bool buildworldstate()
	{
		worldstate &ws = *new worldstate;
		loopv(clients)
		{
			clientinfo &ci = *clients[i];
			if(ci.state.aitype != AI_NONE) continue;
			ci.overflow = 0;
			addclientstate(ws, ci);
			loopv(ci.bots)
			{
				clientinfo &bi = *ci.bots[i];
				addclientstate(ws, bi);
				if(bi.posoff >= 0)
				{
					if(ci.posoff < 0) { ci.posoff = bi.posoff; ci.poslen = bi.poslen; }
					else ci.poslen += bi.poslen;
				}
				if(bi.msgoff >= 0)
				{
					if(ci.msgoff < 0) { ci.msgoff = bi.msgoff; ci.msglen = bi.msglen; }
					else ci.msglen += bi.msglen;
				}
			}
		}
		int psize = ws.positions.length(), msize = ws.messages.length();
		if(psize)
		{
			recordpacket(0, ws.positions.getbuf(), psize);
			ucharbuf p = ws.positions.reserve(psize);
			p.put(ws.positions.getbuf(), psize);
			ws.positions.addbuf(p);
		}
		if(msize)
		{
			recordpacket(1, ws.messages.getbuf(), msize);
			ucharbuf p = ws.messages.reserve(msize);
			p.put(ws.messages.getbuf(), msize);
			ws.messages.addbuf(p);
		}
		ws.uses = 0;
		if(psize || msize) loopv(clients)
		{
			clientinfo &ci = *clients[i];
			if(ci.state.aitype != AI_NONE) continue;
			ENetPacket *packet;
			if(psize && (ci.posoff<0 || psize-ci.poslen>0))
			{
				packet = enet_packet_create(&ws.positions[ci.posoff<0 ? 0 : ci.posoff+ci.poslen],
											ci.posoff<0 ? psize : psize-ci.poslen,
											ENET_PACKET_FLAG_NO_ALLOCATE);
				sendpacket(ci.clientnum, 0, packet);
				if(!packet->referenceCount) enet_packet_destroy(packet);
				else { ++ws.uses; packet->freeCallback = cleanworldstate; }
			}

			if(msize && (ci.msgoff<0 || msize-ci.msglen>0))
			{
				packet = enet_packet_create(&ws.messages[ci.msgoff<0 ? 0 : ci.msgoff+ci.msglen],
											ci.msgoff<0 ? msize : msize-ci.msglen,
											(reliablemessages ? ENET_PACKET_FLAG_RELIABLE : 0) | ENET_PACKET_FLAG_NO_ALLOCATE);
				sendpacket(ci.clientnum, 1, packet);
				if(!packet->referenceCount) enet_packet_destroy(packet);
				else { ++ws.uses; packet->freeCallback = cleanworldstate; }
			}
		}
		reliablemessages = false;
		if(!ws.uses)
		{
			delete &ws;
			return false;
		}
		else
		{
			worldstates.add(&ws);
			return true;
		}
	}

	bool sendpackets(bool force)
	{
		if(clients.empty() || (!hasnonlocalclients() && !demorecord)) return false;
		enet_uint32 curtime = enet_time_get()-lastsend;
		if(curtime<33 && !force) return false;
		bool flush = buildworldstate();
		lastsend += curtime - (curtime%33);
		return flush;
	}

	template<class T>
	void sendstate(gamestate &gs, T &p)
	{
		putint(p, gs.lifesequence);
		putint(p, gs.health);
		putint(p, gs.maxhealth);
		putint(p, gs.armour);
		putint(p, gs.armourtype);
		putint(p, gs.gunselect);
		loopi(GUN_PISTOL-GUN_SG+1) putint(p, gs.ammo[GUN_SG+i]);
	}

	void spawnstate(clientinfo *ci)
	{
		gamestate &gs = ci->state;
		gs.spawnstate(gamemode);
		gs.lifesequence = (gs.lifesequence + 1)&0x7F;
	}

	void sendspawn(clientinfo *ci)
	{
		gamestate &gs = ci->state;
		spawnstate(ci);
		sendf(ci->ownernum, 1, "rii7v", N_SPAWNSTATE, ci->clientnum, gs.lifesequence,
			gs.health, gs.maxhealth,
			gs.armour, gs.armourtype,
			gs.gunselect, GUN_PISTOL-GUN_SG+1, &gs.ammo[GUN_SG]);
		gs.lastspawn = gamemillis;
	}

	void sendinitclient(clientinfo *ci);

	void sendClientInitialization(clientinfo *ci)
	{
		packetbuf p(MAXTRANS, ENET_PACKET_FLAG_RELIABLE);
		int chan = initclientpacket(p, ci);
		sendpacket(ci->clientnum, chan, p.finalize());
		ci->connectstage = 2;
		if (ci->state.state != CS_INVISIBLE)
		{
			sendinitclient(ci);
		}
		SbPy::triggerEventf("client_connect", "i", ci->clientnum);
	}

	void reinitclients()
	{
		loopv(clients)
		{
			SbPy::triggerEventf("client_reinit", "i", clients[i]->clientnum);
		}
	}

	void sendwelcome(clientinfo *ci)
	{
		packetbuf p(MAXTRANS, ENET_PACKET_FLAG_RELIABLE);
		int chan = welcomepacket(p, ci);
		sendpacket(ci->clientnum, chan, p.finalize());
		ci->connectstage = 1;
	}

	void putinitclient(clientinfo *ci, packetbuf &p)
	{
		if(ci->state.aitype != AI_NONE)
		{
			putint(p, N_INITAI);
			putint(p, ci->clientnum);
			putint(p, ci->ownernum);
			putint(p, ci->state.aitype);
			putint(p, ci->state.skill);
			putint(p, ci->playermodel);
			sendstring(ci->name, p);
			sendstring(ci->team, p);
		}
		else
		{
			putint(p, N_INITCLIENT);
			putint(p, ci->clientnum);
			sendstring(ci->name, p);
			sendstring(ci->team, p);
			putint(p, ci->playermodel);
		}
	}

	void welcomeinitclient(packetbuf &p, int exclude = -1)
	{
		loopv(clients)
		{
			clientinfo *ci = clients[i];
			if(ci->connectstage < 2 || ci->clientnum == exclude || ci->state.state == CS_INVISIBLE) continue;
			putinitclient(ci, p);
		}
	}

	int initclientpacket(packetbuf &p, clientinfo *ci)
	{
		int hasmap = (m_edit && (clients.length()>1 || (ci && ci->local))) || (smapname[0] && (!m_timed || gamemillis<gamelimit || (ci && ci->state.state==CS_SPECTATOR && !ci->privilege && !ci->local) || numclients(ci ? ci->clientnum : -1, true, true, true)));
		if(hasmap)
		{
			putint(p, N_MAPCHANGE);
			sendstring(smapname, p);
			putint(p, gamemode);
			putint(p, notgotitems ? 1 : 0);
			if(!ci || (m_timed && smapname[0]))
			{
				putint(p, N_TIMEUP);
				putint(p, gamemillis < gamelimit && !interm ? max((gamelimit - gamemillis)/1000, 1) : 0);
			}
			if(!notgotitems)
			{
				putint(p, N_ITEMLIST);
				loopv(sents) if(sents[i].spawned)
				{
					putint(p, i);
					putint(p, sents[i].type);
				}
				putint(p, -1);
			}
		}
		if(currentmaster >= 0 || mastermode != MM_OPEN)
		{
			putint(p, N_CURRENTMASTER);
			putint(p, currentmaster);
			clientinfo *m = currentmaster >= 0 ? getinfo(currentmaster) : NULL;
			putint(p, m ? m->privilege : 0);
			putint(p, mastermode);
		}
		if(gamepaused)
		{
			putint(p, N_PAUSEGAME);
			putint(p, 1);
		}
		if(ci)
		{
			putint(p, N_SETTEAM);
			putint(p, ci->clientnum);
			sendstring(ci->team, p);
			putint(p, -1);
		}
		if(ci && (m_demo || m_mp(gamemode)) && ci->state.state<CS_SPECTATOR)
		{
			if(smode && !smode->canspawn(ci, true))
			{
				ci->state.state = CS_DEAD;
				putint(p, N_FORCEDEATH);
				putint(p, ci->clientnum);
				sendf(-1, 1, "ri2x", N_FORCEDEATH, ci->clientnum, ci->clientnum);
			}
			else
			{
				gamestate &gs = ci->state;
				spawnstate(ci);
				putint(p, N_SPAWNSTATE);
				putint(p, ci->clientnum);
				sendstate(gs, p);
				gs.lastspawn = gamemillis;
			}
		}
		if(ci && ci->state.state==CS_SPECTATOR)
		{
			putint(p, N_SPECTATOR);
			putint(p, ci->clientnum);
			putint(p, 1);
			sendf(-1, 1, "ri3x", N_SPECTATOR, ci->clientnum, 1, ci->clientnum);
		}
		if(!ci || clients.length()>1)
		{
			putint(p, N_RESUME);
			loopv(clients)
			{
				clientinfo *oi = clients[i];
				if(oi->state.state == CS_INVISIBLE) continue;
				if(ci && oi->clientnum==ci->clientnum) continue;
				putint(p, oi->clientnum);
				putint(p, oi->state.state);
				putint(p, oi->state.frags);
				putint(p, oi->state.flags);
				putint(p, oi->state.quadmillis);
				sendstate(oi->state, p);
			}
			putint(p, -1);
			welcomeinitclient(p, ci ? ci->clientnum : -1);
		}
		if(smode) smode->initclient(ci, p, true);
		return 1;
	}

	int welcomepacket(packetbuf &p, clientinfo *ci)
	{
		int hasmap = (m_edit && (clients.length()>1 || (ci && ci->local))) || (smapname[0] && (!m_timed || gamemillis<gamelimit || (ci && ci->state.state==CS_SPECTATOR && !ci->privilege && !ci->local) || numclients(ci ? ci->clientnum : -1, true, true, true)));
		putint(p, N_WELCOME);
		putint(p, hasmap); //always tell the client if we have a map but don't send what it is until after a delay
		return 1;
	}

	bool restorescore(clientinfo *ci)
	{
		//if(ci->local) return false;
		savedscore &sc = findscore(ci, false);
		if(&sc)
		{
			sc.restore(ci->state);
			return true;
		}
		return false;
	}

	void sendresume(clientinfo *ci)
	{
		gamestate &gs = ci->state;
		if(ci->state.state != CS_INVISIBLE)
		sendf(-1, 1, "ri3i9vi", N_RESUME, ci->clientnum,
			gs.state, gs.frags, gs.flags, gs.quadmillis,
			gs.lifesequence,
			gs.health, gs.maxhealth,
			gs.armour, gs.armourtype,
			gs.gunselect, GUN_PISTOL-GUN_SG+1, &gs.ammo[GUN_SG], -1);
	}

	void sendinitclient(clientinfo *ci)
	{
		packetbuf p(MAXTRANS, ENET_PACKET_FLAG_RELIABLE);
		putinitclient(ci, p);
		sendpacket(-1, 1, p.finalize(), ci->clientnum);
	}

	void changemap(const char *s, int mode)
	{
		SbPy::triggerEventf("map_changed_pre", "");
		stopdemo();
		if(smode) smode->reset(false);
		aiman::clearai();

		mapreload = false;
		gamemode = mode;
		gamemillis = 0;
		gamelimit = (m_overtime ? 15 : 10)*60000;
		interm = 0;
		copystring(smapname, s);
		resetitems();
		notgotitems = true;
		scores.setsize(0);
		loopv(clients)
		{
			clientinfo *ci = clients[i];
			ci->state.timeplayed += lastmillis - ci->state.lasttimeplayed;
		}

		if(!m_mp(gamemode)) kicknonlocalclients(DISC_PRIVATE);

		if(m_teammode) autoteam();

		if(m_capture) smode = &capturemode;
		else if(m_ctf) smode = &ctfmode;
		else smode = NULL;
		if(smode) smode->reset(false);

		if(m_timed && smapname[0]) sendf(-1, 1, "ri2", N_TIMEUP, gamemillis < gamelimit && !interm ? max((gamelimit - gamemillis)/1000, 1) : 0);
		loopv(clients)
		{
			clientinfo *ci = clients[i];
			ci->mapchange();
			ci->state.lasttimeplayed = lastmillis;
			if(m_mp(gamemode) && ci->state.state!=CS_SPECTATOR) sendspawn(ci);
		}

		aiman::changemap();

		if(m_demo)
		{
			if(clients.length()) setupdemoplayback();
		}
		else if(demonextmatch || persistentdemos)
		{
			demonextmatch = false;
			setupdemorecord();
		}
		SbPy::triggerEventf("map_changed", "si", smapname, mode);
	}

	void setmap(const char *s, int mode)
	{
		sendf(-1, 1, "risii", N_MAPCHANGE, s, mode, 1);
		changemap(s, mode);
	}

	void setmastermode(int mm)
	{
		mastermode = mm;
		sendf(-1, 1, "rii", N_MASTERMODE, mastermode);
		SbPy::triggerEventf("server_mastermode_changed", "i", mastermode);
	}

	void forcemap(const char *map, int mode)
	{
		stopdemo();
		sendf(-1, 1, "risii", N_MAPCHANGE, map, mode, 1);
		changemap(map, mode);
	}

	void setTimeLeft(int milliseconds)
	{
		gamelimit = gamemillis + milliseconds + 1;
		sendf(-1, 1, "ri2", N_TIMEUP, gamemillis < gamelimit && !interm ? max((gamelimit - gamemillis)/1000, 1) : 0);
	}

	void checkintermission()
	{
		if(gamemillis >= gamelimit && !interm)
		{
			SbPy::triggerEventf("intermission_begin", "");
			sendf(-1, 1, "ri2", N_TIMEUP, 0);
			if(smode) smode->intermission();
			interm = gamemillis + intermissionlength;
		}
	}

	void startintermission() { gamelimit = min(gamelimit, gamemillis); checkintermission(); }

	void dodamage(clientinfo *target, clientinfo *actor, int damage, int gun, const vec &hitpush = vec(0, 0, 0))
	{
		if(actor->state.state == CS_INVISIBLE) return;
		gamestate &ts = target->state;
		ts.dodamage(damage);
		SbPy::triggerEventf("client_inflict_damage", "iii", actor->clientnum, gun, damage);
		actor->state.damage += damage;
		sendf(-1, 1, "ri6", N_DAMAGE, target->clientnum, actor->clientnum, damage, ts.armour, ts.health);
		if(target==actor) target->setpushed();
		else if(target!=actor && !hitpush.iszero())
		{
			ivec v = vec(hitpush).rescale(DNF);
			sendf(ts.health<=0 ? -1 : target->ownernum, 1, "ri7", N_HITPUSH, target->clientnum, gun, damage, v.x, v.y, v.z);
			target->setpushed();
		}
		if(ts.health<=0)
		{
			target->state.deaths++;
			if(isteam(actor->team, target->team))
			{
				if(actor->clientnum != target->clientnum)
				{
					actor->state.teamkills++;
				}
			}

			int fragvalue = smode ? smode->fragvalue(target, actor) : (target==actor || isteam(target->team, actor->team) ? -1 : 1);
			actor->state.frags += fragvalue;
			if(fragvalue>0)
			{
				int friends = 0, enemies = 0; // note: friends also includes the fragger
				if(m_teammode) loopv(clients) if(strcmp(clients[i]->team, actor->team)) enemies++; else friends++;
				else { friends = 1; enemies = clients.length()-1; }
				actor->state.effectiveness += fragvalue*friends/float(max(enemies, 1));
			}
			sendf(-1, 1, "ri4", N_DIED, target->clientnum, actor->clientnum, actor->state.frags);
			target->position.setsize(0);
			if(smode) smode->died(target, actor);
			ts.state = CS_DEAD;
			ts.lastdeath = gamemillis;

			//moved these events down here for clarity
			//hopefully the order of these things isn't important to any plugins
			if(actor->clientnum == target->clientnum)
			{
				SbPy::triggerEventf("client_suicide", "i", actor->clientnum);
			}
			else if(isteam(actor->team, target->team))
			{
				SbPy::triggerEventf("client_teamkill", "ii", actor->clientnum, target->clientnum);
			}
			else
			{
				SbPy::triggerEventf("client_frag", "ii", actor->clientnum, target->clientnum);
			}
			// don't issue respawn yet until DEATHMILLIS has elapsed
			// ts.respawn();
		}
	}

	void suicide(clientinfo *ci)
	{
		gamestate &gs = ci->state;
		if(gs.state!=CS_ALIVE) return;
		ci->state.frags += smode ? smode->fragvalue(ci, ci) : -1;
		ci->state.deaths++;
		if(ci->state.state != CS_INVISIBLE)
		{
			sendf(-1, 1, "ri4", N_DIED, ci->clientnum, ci->clientnum, gs.frags);
	}
		ci->position.setsize(0);
		if(smode) smode->died(ci, NULL);
		gs.state = CS_DEAD;
		gs.respawn();
	}


	void suicideevent::process(clientinfo *ci)
	{
		suicide(ci);
	}

	void explodeevent::process(clientinfo *ci)
	{
		gamestate &gs = ci->state;
		switch(gun)
		{
			case GUN_RL:
				if(!gs.rockets.remove(id)) return;
				break;

			case GUN_GL:
				if(!gs.grenades.remove(id)) return;
				break;

			default:
				return;
		}
		if(ci->state.state != CS_INVISIBLE)
		{
				sendf(-1, 1, "ri4x", N_EXPLODEFX, ci->clientnum, gun, id, ci->ownernum);
		}
		gs.shots++;
		if (!allowshooting) return;
		loopv(hits)
		{
			hitinfo &h = hits[i];
			clientinfo *target = getinfo(h.target);
			if(!target || target->state.state!=CS_ALIVE || h.lifesequence!=target->state.lifesequence || h.dist<0 || h.dist>RL_DAMRAD) continue;

			bool dup = false;
			loopj(i) if(hits[j].target==h.target) { dup = true; break; }
			if(dup) continue;

			gs.hits++;
			int damage = guns[gun].damage;
			if(gs.quadmillis) damage *= 4;
			damage = int(damage*(1-h.dist/RL_DISTSCALE/RL_DAMRAD));
			if(gun==GUN_RL && target==ci) damage /= RL_SELFDAMDIV;
			dodamage(target, ci, damage, gun, h.dir);
		}
	}

	void shotevent::process(clientinfo *ci)
	{
		gamestate &gs = ci->state;
		int wait = millis - gs.lastshot;
		if(!gs.isalive(gamemillis) ||
		  wait<gs.gunwait ||
		  gun<GUN_FIST || gun>GUN_PISTOL ||
		  gs.ammo[gun]<=0 || (guns[gun].range && from.dist(to) > guns[gun].range + 1))
		  return;
		if(gun!=GUN_FIST) gs.ammo[gun]--;
		gs.lastshot = millis;
		gs.gunwait = guns[gun].attackdelay;
		if(ci->state.state != CS_INVISIBLE)
		{
		sendf(-1, 1, "rii9x", N_SHOTFX, ci->clientnum, gun, id,
				int(from.x*DMF), int(from.y*DMF), int(from.z*DMF),
				int(to.x*DMF), int(to.y*DMF), int(to.z*DMF),
				ci->ownernum);
	}
		int tempdamage = guns[gun].damage*(gs.quadmillis ? 4 : 1)*(gun==GUN_SG ? SGRAYS : 1);
		gs.shotdamage += tempdamage;
		SbPy::triggerEventf("client_spend_damage", "iii", ci->clientnum, gun, tempdamage);
		gs.shots++;
		if (!allowshooting) return;
		switch(gun)
		{
			case GUN_RL: gs.rockets.add(id); break;
			case GUN_GL: gs.grenades.add(id); break;
			default:
			{
				int totalrays = 0, maxrays = gun==GUN_SG ? SGRAYS : 1;
				loopv(hits)
				{
					hitinfo &h = hits[i];
					clientinfo *target = getinfo(h.target);
					if(!target || target->state.state!=CS_ALIVE || h.lifesequence!=target->state.lifesequence || h.rays<1 || h.dist > guns[gun].range + 1) continue;

					gs.hits++;
					totalrays += h.rays;
					if(totalrays>maxrays) continue;
					int damage = h.rays*guns[gun].damage;
					if(gs.quadmillis) damage *= 4;
					dodamage(target, ci, damage, gun, h.dir);
				}
				break;
			}
		}
	}

	void pickupevent::process(clientinfo *ci)
	{
		gamestate &gs = ci->state;
		if(m_mp(gamemode) && !gs.isalive(gamemillis)) return;
		pickup(ent, ci->clientnum);
	}

	bool gameevent::flush(clientinfo *ci, int fmillis)
	{
		process(ci);
		return true;
	}

	bool timedevent::flush(clientinfo *ci, int fmillis)
	{
		if(millis > fmillis) return false;
		else if(millis >= ci->lastevent)
		{
			ci->lastevent = millis;
			process(ci);
		}
		return true;
	}

	void clearevent(clientinfo *ci)
	{
		delete ci->events.remove(0);
	}

	void flushevents(clientinfo *ci, int millis)
	{
		while(ci->events.length())
		{
			gameevent *ev = ci->events[0];
			if(ev->flush(ci, millis)) clearevent(ci);
			else break;
		}
	}

	void processevents()
	{
		loopv(clients)
		{
			clientinfo *ci = clients[i];
			if(curtime>0 && ci->state.quadmillis) ci->state.quadmillis = max(ci->state.quadmillis-curtime, 0);
			flushevents(ci, gamemillis);
		}
	}

	void cleartimedevents(clientinfo *ci)
	{
		int keep = 0;
		loopv(ci->events)
		{
			if(ci->events[i]->keepable())
			{
				if(keep < i)
				{
					for(int j = keep; j < i; j++) delete ci->events[j];
					ci->events.remove(keep, i - keep);
					i = keep;
				}
				keep = i+1;
				continue;
			}
		}
		while(ci->events.length() > keep) delete ci->events.pop();
		ci->timesync = false;
	}

	bool ispaused() { return gamepaused; }

	void serverupdate()
	{
		if(!gamepaused) gamemillis += curtime;

		if(m_demo) readdemo();
		else if(!gamepaused && (!m_timed || gamemillis < gamelimit))
		{
			processevents();
			if(curtime)
			{
				loopv(sents) if(sents[i].spawntime) // spawn entities when timer reached
				{
					int oldtime = sents[i].spawntime;
					sents[i].spawntime -= curtime;
					if(sents[i].spawntime<=0)
					{
						sents[i].spawntime = 0;
						sents[i].spawned = true;
						sendf(-1, 1, "ri2", N_ITEMSPAWN, i);
					}
					else if(sents[i].spawntime<=10000 && oldtime>10000 && (sents[i].type==I_QUAD || sents[i].type==I_BOOST))
					{
						sendf(-1, 1, "ri2", N_ANNOUNCE, sents[i].type);
					}
				}
			}
			aiman::checkai();
			if(smode) smode->update();
		}

		loopv(connects)
		{
			if(totalmillis-connects[i]->connectmillis>15000)
			{
				disconnect_client(connects[i]->clientnum, DISC_TIMEOUT);
				continue;
			}
		}

		if(!SbPy::update())
		{
			exit(1);
		}

		if(!gamepaused && m_timed && smapname[0] && gamemillis-curtime>0) checkintermission();
		if(interm > 0 && gamemillis>interm && !persistentintermission)
		{
			if(demorecord) enddemorecord();
			interm = -1;
			SbPy::triggerEventf("intermission_ended", "");
			//if(clients.length()) sendf(-1, 1, "ri", N_MAPRELOAD);
		}
	}

	void checkdisconnects(bool last)
	{
		loopv(clients)
		{
			if(clients[i]->disconnect_reason >= DISC_NONE || last)
			{
				disconnect_client(clients[i]->clientnum, clients[i]->disconnect_reason >= DISC_NONE ? clients[i]->disconnect_reason : DISC_NONE);
			}
		}
	}

	void sendmapreload()
	{
		if(clients.length()) sendf(-1, 1, "ri", N_MAPRELOAD);
	}

	struct crcinfo
	{
		int crc, matches;

		crcinfo(int crc, int matches) : crc(crc), matches(matches) {}

		static int compare(const crcinfo *x, const crcinfo *y)
		{
			if(x->matches > y->matches) return -1;
			if(x->matches < y->matches) return 1;
			return 0;
		}
	};

	void sendservinfo(clientinfo *ci)
	{
		sendf(ci->clientnum, 1, "ri5s", N_SERVINFO, ci->clientnum, PROTOCOL_VERSION, ci->sessionid, serverprivate, serverdesc);
	}

	void setinvisible(clientinfo *ci, bool val)
	{
		if (ci->state.state == CS_INVISIBLE && !val)
		{
			if(mastermode==MM_OPEN)
			{
				ci->state.state = CS_DEAD;
				ci->state.respawn();
				ci->state.lasttimeplayed = lastmillis;
				aiman::addclient(ci);
			}
			else
			{
				ci->state.state = CS_SPECTATOR;
			}
			sendinitclient(ci);
			aiman::addclient(ci);
		}
		if (ci->state.state != CS_INVISIBLE && val)
		{
			sendf(-1, 1, "ri2", N_CDIS, ci->clientnum);
			ci->state.state = CS_INVISIBLE;
			ci->state.timeplayed += lastmillis - ci->state.lasttimeplayed;
			aiman::removeai(ci);
		}
	}

	bool spectate(clientinfo *spinfo, bool val)
	{
		bool spectated = false, unspectated = false;
		if(spinfo->state.state!=CS_SPECTATOR && val)
		{
			if(spinfo->state.state==CS_ALIVE) suicide(spinfo);
			if(smode) smode->leavegame(spinfo);
			spinfo->state.state = CS_SPECTATOR;
			spinfo->state.timeplayed += lastmillis - spinfo->state.lasttimeplayed;
			if(!spinfo->local && !spinfo->privilege) aiman::removeai(spinfo);
			spectated = true;
		}
		else if(spinfo->state.state==CS_SPECTATOR && !val)
		{
			spinfo->state.state = CS_DEAD;
			spinfo->state.respawn();
			spinfo->state.lasttimeplayed = lastmillis;
			aiman::addclient(spinfo);
			unspectated = true;
		}
		else
			return false;
		sendf(-1, 1, "ri3", N_SPECTATOR, spinfo->clientnum, val);
		if(!val && mapreload && !spinfo->privilege) sendf(spinfo->clientnum, 1, "ri", N_MAPRELOAD);
		if(spectated)
			SbPy::triggerEventf("client_spectate", "i", spinfo->clientnum);
		else if(unspectated)
			SbPy::triggerEventf("client_unspectated", "i", spinfo->clientnum);
		return true;
	}

	void noclients()
	{
		aiman::clearai();
		SbPy::triggerEventf("no_clients", "");
	}

	bool getbysessionid(int sessionid)
	{
		loopv(clients) if(clients[i]->sessionid == sessionid) return clients[i];
		return NULL;
	}

	int clientconnect(int n, uint ip)
	{
		clientinfo *ci = getinfo(n);
		ci->clientnum = ci->ownernum = n;
		ci->connectmillis = totalmillis;

		//get a new unique sessionid
		//ci->sessionid = (rnd(0x1000000)*((totalmillis%10000)+1))&0xFFFFFF;
		ci->sessionid = (((unsigned long) &ci)%10000)+rnd(0x1000000);
		while(getbysessionid(ci->sessionid))
		{
			ci->sessionid = (((unsigned long) &ci)%10000)+rnd(0x1000000);
		}

		connects.add(ci);
		sendservinfo(ci);
		return DISC_NONE;
	}

	void clientdisconnect(int n)
	{
		clientinfo *ci = getinfo(n);
		SbPy::triggerEventf("client_disconnect", "i", n);
		if(ci->connected)
		{
			if(ci->privilege) resetpriv(ci);
			if(smode) smode->leavegame(ci, true);
			ci->state.timeplayed += lastmillis - ci->state.lasttimeplayed;
			savescore(ci);
			if(ci->state.state != CS_INVISIBLE)
			{
				sendf(-1, 1, "ri2", N_CDIS, n);
			}
			clients.removeobj(ci);
			aiman::removeai(ci);
			if(!numclients(-1, false, true)) noclients();
		}
		else
		{
			connects.removeobj(ci);
		}
		SbPy::triggerEventf("client_disc", "i", n);
	}

	int reserveclients() { return 3; }

	bool allowbroadcast(int n)
	{
		clientinfo *ci = getinfo(n);
		return ci && ci->connected && ci->connectstage == 2;
	}

	clientinfo *findauth(uint id)
	{
		loopv(clients) if(clients[i]->authreq == id) return clients[i];
		return NULL;
	}

	void authchallenged(uint id, const char *val)
	{
		clientinfo *ci = findauth(id);
		if(!ci) return;
		sendf(ci->clientnum, 1, "risis", N_AUTHCHAL, "", id, val);
	}

	void challengeauth(clientinfo *ci, uint id, const char *domain, const char *val)
	{
		if(!ci) return;
		sendf(ci->clientnum, 1, "risis", N_AUTHCHAL, domain, id, val);
	}

	void receivefile(int sender, uchar *data, int len)
	{
		if(!m_edit || len > 1024*1024) return;
		clientinfo *ci = getinfo(sender);
		if(ci->state.state==CS_SPECTATOR && !ci->privilege && !ci->local) return;
		if(mapdata) DELETEP(mapdata);
		if(!len) return;
		mapdata = opentempfile("mapdata", "w+b");
		if(!mapdata) { sendf(sender, 1, "ris", N_SERVMSG, "failed to open temporary file for map"); return; }
		mapdata->write(data, len);

		SbPy::triggerEventf("client_uploaded_map", "ip", sender, Py_BuildValue("s#", data, len));
	}

	void sendclipboard(clientinfo *ci)
	{
		if(!ci->lastclipboard || !ci->clipboard) return;
		bool flushed = false;
		loopv(clients)
		{
			clientinfo &e = *clients[i];
			if(e.clientnum != ci->clientnum && e.needclipboard >= ci->lastclipboard)
			{
				if(!flushed) { flushserver(true); flushed = true; }
				sendpacket(e.clientnum, 1, ci->clipboard);
			}
		}
	}

	void parsepacket(int sender, int chan, packetbuf &p)	// has to parse exactly each byte of the packet
	{
		if(sender<0) return;
		char text[MAXTRANS];
		int type;
		clientinfo *ci = sender>=0 ? getinfo(sender) : NULL, *cq = ci, *cm = ci;
		if(ci && !ci->connected)
		{
			if(chan==0) return;
			else if(chan!=1 || getint(p)!=N_CONNECT) { disconnect_client(sender, DISC_TAGT); return; }
			else
			{
				getstring(text, p);
				filtertext(text, text, false, MAXNAMELEN);
				if(!text[0]) copystring(text, "unnamed");
				copystring(ci->name, text, MAXNAMELEN+1);

				getstring(text, p);

				copystring(ci->connectpwd, text, strlen(text));

				SbPy::triggerEventf("client_init", "i", ci->clientnum);

				ci->playermodel = getint(p);

				if(m_demo) enddemoplayback();

				connects.removeobj(ci);
				clients.add(ci);

				ci->connected = true;
				ci->needclipboard = totalmillis;

				ci->state.state = CS_SPECTATOR;

				ci->state.lasttimeplayed = lastmillis;

				const char *worst = m_teammode ? chooseworstteam(text, ci) : NULL;
				copystring(ci->team, worst ? worst : "good", MAXTEAMLEN+1);

				sendwelcome(ci);
				if(restorescore(ci)) sendresume(ci);

				aiman::addclient(ci);

				if(m_demo) setupdemoplayback();

				SbPy::triggerEventf("client_connect_pre", "i", ci->clientnum);
			}
		}
		else if(chan==2)
		{
			receivefile(sender, p.buf, p.maxlen);
			return;
		}

		if(p.packet->flags&ENET_PACKET_FLAG_RELIABLE) reliablemessages = true;
		#define QUEUE_AI clientinfo *cm = cq;
		#define QUEUE_MSG { if(cm && (!cm->local || demorecord || hasnonlocalclients())) while(curmsg<p.length()) cm->messages.add(p.buf[curmsg++]); }
		#define QUEUE_BUF(body) { \
			if(cm && (!cm->local || demorecord || hasnonlocalclients())) \
			{ \
				curmsg = p.length(); \
				{ body; } \
			} \
		}

		#define QUEUE_INT(n) QUEUE_BUF(putint(cm->messages, n))
		#define QUEUE_UINT(n) QUEUE_BUF(putuint(cm->messages, n))
		#define QUEUE_STR(text) QUEUE_BUF(sendstring(text, cm->messages))
		int curmsg;
		while((curmsg = p.length()) < p.maxlen) switch(type = checktype(getint(p), ci))
		{
			case N_POS:
			{
				int pcn = getuint(p);
				p.get();
				uint flags = getuint(p);
				clientinfo *cp = getinfo(pcn);
				if(cp && pcn != sender && cp->ownernum != sender) cp = NULL;
				vec pos;
				loopk(3)
				{
					int n = p.get(); n |= p.get()<<8; if(flags&(1<<k)) { n |= p.get()<<16; if(n&0x800000) n |= -1<<24; }
					pos[k] = n/DMF;
				}
				loopk(3) p.get();
				int mag = p.get(); if(flags&(1<<3)) mag |= p.get()<<8;
				int dir = p.get(); dir |= p.get()<<8;
				vec vel = vec((dir%360)*RAD, (clamp(dir/360, 0, 180)-90)*RAD).mul(mag/DVELF);
				if(flags&(1<<4))
				{
					p.get(); if(flags&(1<<5)) p.get();
					if(flags&(1<<6)) loopk(2) p.get();
				}
				if(cp)
				{
					if(!ci->local && !m_edit && max(vel.magnitude2(), (float)fabs(vel.z)) >= 180)
						cp->setexceeded();
					if((!ci->local || demorecord || hasnonlocalclients()) && (cp->state.state==CS_ALIVE || cp->state.state==CS_EDITING))
					{
						cp->position.setsize(0);
						while(curmsg<p.length()) cp->position.add(p.buf[curmsg++]);
					}
					if(smode && cp->state.state==CS_ALIVE) smode->moved(cp, cp->state.o, cp->gameclip, pos, (flags&0x80)!=0);
					cp->state.o = pos;
					cp->gameclip = (flags&0x80)!=0;
				}
				break;
			}

			case N_TELEPORT:
			{
				int pcn = getint(p), teleport = getint(p), teledest = getint(p);
				clientinfo *cp = getinfo(pcn);
				if(cp && pcn != sender && cp->ownernum != sender) cp = NULL;
				if(cp && (!ci->local || demorecord || hasnonlocalclients()) && (cp->state.state==CS_ALIVE || cp->state.state==CS_EDITING))
				{
					flushclientposition(*cp);
					if(cp->state.state != CS_INVISIBLE)
					{
						sendf(-1, 0, "ri4x", N_TELEPORT, pcn, teleport, teledest, cp->ownernum);
					}
					SbPy::triggerEventf("client_teleport", "iii", cp->clientnum, teleport, teledest);
				}
				break;
			}

			case N_JUMPPAD:
			{
				int pcn = getint(p), jumppad = getint(p);
				clientinfo *cp = getinfo(pcn);
				if(cp && pcn != sender && cp->ownernum != sender) cp = NULL;
				if(cp && (!ci->local || demorecord || hasnonlocalclients()) && (cp->state.state==CS_ALIVE || cp->state.state==CS_EDITING))
				{
					cp->setpushed();
					flushclientposition(*cp);
					if(cp->state.state != CS_INVISIBLE)
					{
						sendf(-1, 0, "ri3x", N_JUMPPAD, pcn, jumppad, cp->ownernum);
					}
					SbPy::triggerEventf("client_jumppad", "ii", cp->clientnum, jumppad);
				}
				break;
			}

			case N_FROMAI:
			{
				int qcn = getint(p);
				if(qcn < 0) cq = ci;
				else
				{
					cq = getinfo(qcn);
					if(cq && qcn != sender && cq->ownernum != sender) cq = NULL;
				}
				break;
			}

			case N_EDITMODE:
			{
				int val = getint(p);
				if(!m_edit)
				{
					SbPy::triggerEventf("client_cheat", "is", ci->clientnum, "N_EDITMODE during non-edit gamemode.");
					break;
				}
				if(val ? ci->state.state!=CS_ALIVE && ci->state.state!=CS_DEAD : ci->state.state!=CS_EDITING) break;
				if(smode)
				{
					if(val) smode->leavegame(ci);
					else smode->entergame(ci);
				}
				if(val)
				{
					ci->state.editstate = ci->state.state;
					ci->state.state = CS_EDITING;
					ci->events.setsize(0);
					ci->state.rockets.reset();
					ci->state.grenades.reset();
				}
				else ci->state.state = ci->state.editstate;
				QUEUE_MSG;
				break;
			}

			case N_MAPCRC:
			{
				getstring(text, p);
				int crc = getint(p);
				if(!ci) break;
				if(strcmp(text, smapname))
				{
					if(ci->clientmap[0])
					{
						ci->clientmap[0] = '\0';
						ci->mapcrc = 0;
					}
					else if(ci->mapcrc > 0) ci->mapcrc = 0;
					break;
				}
				copystring(ci->clientmap, text);
				ci->mapcrc = text[0] ? crc : 1;
				SbPy::triggerEventf("client_map_crc", "ii", ci->clientnum, ci->mapcrc);
				break;
			}

			case N_CHECKMAPS:
				SbPy::triggerEventf("client_checkmaps", "i", sender);
				break;

			case N_TRYSPAWN:
				if(!ci || !cq || cq->state.state!=CS_DEAD || cq->state.lastspawn>=0 || (smode && !smode->canspawn(cq))) break;

				if(cq->state.lastdeath)
				{
					flushevents(cq, cq->state.lastdeath + DEATHMILLIS);
					cq->state.respawn();
				}
				cleartimedevents(cq);
				sendspawn(cq);
				break;

			case N_GUNSELECT:
			{
				int gunselect = getint(p);
				if(!cq || cq->state.state!=CS_ALIVE) break;
				if(gunselect<GUN_FIST || gunselect>GUN_PISTOL)
				{
					SbPy::triggerEventf("client_cheat", "is", ci->clientnum, "Weapon out of valid range.");
					break;
				}
				cq->state.gunselect = gunselect;
				QUEUE_AI;
				QUEUE_MSG;
				break;
			}

			case N_SPAWN:
			{
				int ls = getint(p), gunselect = getint(p);
				if(!cq || (cq->state.state!=CS_ALIVE && cq->state.state!=CS_DEAD) || ls!=cq->state.lifesequence || cq->state.lastspawn<0) break;
				if(gunselect<GUN_FIST || gunselect>GUN_PISTOL)
				{
					SbPy::triggerEventf("client_cheat", "is", ci->clientnum, "Weapon out of valid range.");
					break;
				}
				cq->state.lastspawn = -1;
				cq->state.state = CS_ALIVE;
				cq->state.gunselect = gunselect;
				cq->exceeded = 0;
				if(smode) smode->spawned(cq);
				QUEUE_AI;
				QUEUE_BUF({
					putint(cm->messages, N_SPAWN);
					sendstate(cq->state, cm->messages);
				});
				break;
			}

			case N_SUICIDE:
			{
				if(cq)
				{
					cq->addevent(new suicideevent);
					SbPy::triggerEventf("client_suicide", "i", cq->clientnum);
				}
				break;
			}

			case N_SHOOT:
			{
				shotevent *shot = new shotevent;
				shot->id = getint(p);
				shot->millis = cq ? cq->geteventmillis(gamemillis, shot->id) : 0;
				shot->gun = getint(p);
				if(shot->gun<GUN_FIST || shot->gun>GUN_PISTOL)
				{
					SbPy::triggerEventf("client_cheat", "is", ci->clientnum, "Weapon out of valid range.");
					while(!p.overread()) getint(p);
					break;
				}
				loopk(3) shot->from[k] = getint(p)/DMF;
				loopk(3) shot->to[k] = getint(p)/DMF;
				SbPy::triggerEventf("client_shot", "iii", cq->clientnum, shot->millis, shot->gun);
				int hits = getint(p);
				loopk(hits)
				{
					if(p.overread()) break;
					hitinfo &hit = shot->hits.add();
					hit.target = getint(p);
					hit.lifesequence = getint(p);
					hit.dist = getint(p)/DMF;
					hit.rays = getint(p);
					loopk(3) hit.dir[k] = getint(p)/DNF;
					SbPy::triggerEventf("client_shot_hit", "iiiii", cq->clientnum, hit.target, hit.lifesequence, hit.dist, hit.rays);
				}
				if(cq)
				{
					cq->addevent(shot);
					cq->setpushed();
				}
				else delete shot;
				break;
			}

			case N_EXPLODE:
			{

				explodeevent *exp = new explodeevent;
				int cmillis = getint(p);
				exp->millis = cq ? cq->geteventmillis(gamemillis, cmillis) : 0;
				exp->gun = getint(p);
				if(exp->gun<GUN_FIST || exp->gun>GUN_PISTOL)
				{
					SbPy::triggerEventf("client_cheat", "is", ci->clientnum, "Weapon out of valid range.");
					while(!p.overread()) getint(p);
					break;
				}
				exp->id = getint(p);
				int hits = getint(p);
				SbPy::triggerEventf("client_explode", "iii", cq->clientnum, exp->millis, exp->gun);
				loopk(hits)
				{
					if(p.overread()) break;
					hitinfo &hit = exp->hits.add();
					hit.target = getint(p);
					hit.lifesequence = getint(p);
					hit.dist = getint(p)/DMF;
					hit.rays = getint(p);
					loopk(3) hit.dir[k] = getint(p)/DNF;
					SbPy::triggerEventf("client_explode_hit", "iiiii", cq->clientnum, hit.target, hit.lifesequence, hit.dist, hit.rays);
				}
				if(cq) cq->addevent(exp);
				else delete exp;
				break;
			}

			case N_ITEMPICKUP:
			{
				int n = getint(p);
				if(!cq) break;
				pickupevent *pickup = new pickupevent;
				pickup->ent = n;
				cq->addevent(pickup);
				SbPy::triggerEventf("client_pickup", "ii", cq->clientnum, pickup->ent);
				break;
			}

			case N_TEXT:
			{
				getstring(text, p);
				filtertext(text, text);
				SbPy::triggerEventf("client_message_pre", "is", ci->clientnum, text);
				break;
			}

			case N_SAYTEAM:
			{
				getstring(text, p);
				filtertext(text, text);
				SbPy::triggerEventf("client_message_team_pre", "is", ci->clientnum, text);
				break;
			}

			case N_SWITCHNAME:
			{
				getstring(text, p);
				SbPy::triggerEventf("client_name_change_pre", "is", ci->clientnum, text);
				break;
			}

			case N_SWITCHMODEL:
			{
				ci->playermodel = getint(p);
				if (ci->state.state != CS_INVISIBLE)
				{
					QUEUE_MSG;
				}
				break;
			}

			case N_SWITCHTEAM:
			{
				getstring(text, p);
				filtertext(text, text, false, MAXTEAMLEN);
				SbPy::triggerEventf("client_switch_team_pre", "is", sender, text);
				break;
			}

			case N_MAPVOTE:
			case N_MAPCHANGE:
			{
				getstring(text, p);
				filtertext(text, text, false);
				int reqmode = getint(p);
				if(type==N_MAPVOTE)
					SbPy::triggerEventf("client_map_vote", "isi", sender, text, reqmode);
				else
					SbPy::triggerEventf("client_map_set", "isi", sender, text, reqmode);
				break;
			}

			case N_ITEMLIST:
			{
				if(m_noitems)
				{
					SbPy::triggerEventf("client_cheat", "is", ci->clientnum, "Sending item list during game mode without items.");
					int n;
					while((n = getint(p))>=0 && n<MAXENTS && !p.overread()) {getint(p);}
					break;
				}

				std::vector<int> item_types;

				int n;
				while((n = getint(p))>=0 && n<MAXENTS && !p.overread())
				{
					while(item_types.size()<n) item_types.push_back(NOTUSED);
					item_types.push_back(getint(p));
				}

				PyObject *pTuple_entities = PyTuple_New(item_types.size());

				n = 0;
				std::vector<int>::const_iterator itr;
				for(itr = item_types.begin(); itr != item_types.end(); itr++)
				{
					PyTuple_SetItem(pTuple_entities, n, PyInt_FromLong(*itr));
					n++;
				}

				SbPy::triggerEventf("client_item_list", "ip", ci->clientnum, pTuple_entities);
				break;
			}

			case N_EDITF:			 // coop editing messages
			case N_EDITT:
			case N_EDITM:
			case N_FLIP:
			//case N_COPY:
			//case N_PASTE:
			case N_ROTATE:
			case N_REPLACE:
			case N_DELCUBE:
			case N_REMIP:
			{
				if (!privateediting) goto genericmsg;
				break;
			}


			case N_EDITENT:
			{
				int i = getint(p);
				loopk(3) getint(p);
				int type = getint(p);
				loopk(5) getint(p);
				if(!ci || ci->state.state>=CS_SPECTATOR) break;
				QUEUE_MSG;
				bool canspawn = canspawnitem(type);
				if(i<MAXENTS && (sents.inrange(i) || canspawnitem(type)))
				{
					server_entity se = { NOTUSED, 0, false };
					while(sents.length()<=i) sents.add(se);
					sents[i].type = type;
					if(canspawn ? !sents[i].spawned : (sents[i].spawned || sents[i].spawntime))
					{
						sents[i].spawntime = canspawn ? 1 : 0;
						sents[i].spawned = false;
					}
				}
				break;
			}

			case N_EDITVAR:
			{
				int type = getint(p);
				getstring(text, p);
				switch(type)
				{
					case ID_VAR: getint(p); break;
					case ID_FVAR: getfloat(p); break;
					case ID_SVAR: getstring(text, p);
				}
				if(ci && ci->state.state == CS_EDITING) QUEUE_MSG;
				break;
			}

			case N_PING:
				sendf(sender, 1, "i2", N_PONG, getint(p));
				break;

			case N_CLIENTPING:
			{
				int ping = getint(p);
				if(ci)
				{
					ci->ping = ping;
					loopv(ci->bots) ci->bots[i]->ping = ping;
				}
				QUEUE_MSG;
				break;
			}

			case N_MASTERMODE:
			{
				int mm = getint(p);
				if(mm>=MM_OPEN && mm<=MM_PRIVATE)
					SbPy::triggerEventf("client_set_mastermode", "ii", ci->clientnum, mm);
				break;
			}

			case N_CLEARBANS:
			{
				SbPy::triggerEventf("client_clear_bans", "i", ci->clientnum);
				break;
			}

			case N_KICK:
			{
				int victim = getint(p);
				if(getclientinfo(victim)) // no bots
				{
					SbPy::triggerEventf("client_kick", "ii", ci->clientnum, victim);
				}
				break;
			}

			case N_SPECTATOR:
			{
				int spectator = getint(p), val = getint(p);
				clientinfo *spinfo = (clientinfo *)getclientinfo(spectator);
				if(!spinfo || (spinfo->state.state==CS_SPECTATOR ? val : !val)) break; // no bots
				SbPy::triggerEventf("client_spectate_pre", "iii", ci->clientnum, spectator, val);
				break;
			}

			case N_SETTEAM:
			{
				int who = getint(p);
				getstring(text, p);
				filtertext(text, text, false, MAXTEAMLEN);
				clientinfo *wi = getinfo(who);
				if(!wi || !strcmp(wi->team, text)) break;
				if(!smode || smode->canchangeteam(wi, wi->team, text))
				{
					SbPy::triggerEventf("client_set_team", "iif", ci->clientnum, who, text);
				}
				break;
			}

			case N_FORCEINTERMISSION:
				if(ci->local && !hasnonlocalclients()) startintermission();
				break;

			case N_RECORDDEMO:
			{
				int val = getint(p);
				SbPy::triggerEventf("client_record_demo", "ib", ci->clientnum, val != 0);
				break;
			}

			case N_STOPDEMO:
			{
				SbPy::triggerEventf("client_stop_demo", "i", ci->clientnum);
				break;
			}

			case N_CLEARDEMOS:
			{
				int demo = getint(p);
				SbPy::triggerEventf("client_clear_demo", "ii", ci->clientnum, demo);
				break;
			}

			case N_LISTDEMOS:
				SbPy::triggerEventf("client_list_demos", "i", ci->clientnum);
				break;

			case N_GETDEMO:
			{
				int demo = getint(p);
				SbPy::triggerEventf("client_get_demo", "ii", ci->clientnum, demo);
				break;
			}

			case N_GETMAP:
				if(mapdata)
				{
					sendfile(sender, 2, mapdata, "ri", N_SENDMAP);
					SbPy::triggerEventf("client_get_map", "i", ci->clientnum);
					ci->connectmillis = totalmillis;
				}
				else sendf(sender, 1, "ris", N_SERVMSG, "no map to send");
				break;

			case N_NEWMAP:
			{
				int size = getint(p);
				if(!ci->privilege && !ci->local && ci->state.state==CS_SPECTATOR) break;
				if(size>=0)
				{
					smapname[0] = '\0';
					resetitems();
					notgotitems = false;
					if(smode) smode->reset(true);
				}
				QUEUE_MSG;
				break;
			}

			case N_SETMASTER:
			{
				int val = getint(p);
				getstring(text, p);
				SbPy::triggerEventf("client_setmaster", "is", ci->clientnum, text);
				break;
			}

			case N_ADDBOT:
			{
				aiman::reqadd(ci, getint(p));
				break;
			}

			case N_DELBOT:
			{
				aiman::reqdel(ci);
				break;
			}

			case N_BOTLIMIT:
			{
				int limit = getint(p);
				SbPy::triggerEventf("client_set_bot_limit", "ii", ci->clientnum, limit);
				break;
			}

			case N_BOTBALANCE:
			{
				int balance = getint(p);
				SbPy::triggerEventf("client_set_bot_limit", "ib", ci->clientnum, balance!=0);
				break;
			}

			case N_AUTHTRY:
			{
				string desc, name;
				getstring(desc, p, sizeof(desc));
				getstring(name, p, sizeof(name));
				SbPy::triggerEventf("client_auth_request", "iss", ci->clientnum, name, desc);
				break;
			}

			case N_AUTHANS:
			{
				string desc, ans;
				getstring(desc, p, sizeof(desc));
				uint id = (uint)getint(p);
				getstring(ans, p, sizeof(ans));
				SbPy::triggerEventf("client_auth_challenge_response", "ics", ci->clientnum, id, ans);
				break;
			}

			case N_PAUSEGAME:
			{
				int val = getint(p);
				SbPy::triggerEventf("client_pause", "ib", ci->clientnum, val != 0);
				break;

			}
			case N_COPY:
				ci->cleanclipboard();
				ci->lastclipboard = totalmillis;
				goto genericmsg;

			case N_PASTE:
				if(ci->state.state!=CS_SPECTATOR) sendclipboard(ci);
				goto genericmsg;

			case N_CLIPBOARD:
			{
				int unpacklen = getint(p), packlen = getint(p);
				ci->cleanclipboard(false);
				if(ci->state.state==CS_SPECTATOR)
				{
					if(packlen > 0) p.subbuf(packlen);
					break;
				}
				if(packlen <= 0 || packlen > (1<<16) || unpacklen <= 0)
				{
					if(packlen > 0) p.subbuf(packlen);
					packlen = unpacklen = 0;
				}
				packetbuf q(32 + packlen, ENET_PACKET_FLAG_RELIABLE);
				putint(q, N_CLIPBOARD);
				putint(q, ci->clientnum);
				putint(q, unpacklen);
				putint(q, packlen);
				if(packlen > 0) p.get(q.subbuf(packlen).buf, packlen);
				ci->clipboard = q.finalize();
				ci->clipboard->referenceCount++;
				break;
			}

			#define PARSEMESSAGES 1
			#include "capture.h"
			#include "ctf.h"
			#undef PARSEMESSAGES

			case -1:
				disconnect_client(sender, DISC_TAGT);
				return;

			case -2:
				disconnect_client(sender, DISC_OVERFLOW);
				return;

			default: genericmsg:
			{
				int size = server::msgsizelookup(type);
				if(size<=0) { disconnect_client(sender, DISC_TAGT); return; }
				loopi(size-1) getint(p);
				if(ci && cq && (ci != cq || ci->state.state!=CS_SPECTATOR)) { QUEUE_AI; QUEUE_MSG; }
				break;
			}
		}
	}

	int laninfoport() { return SAUERBRATEN_LANINFO_PORT; }
	int serverinfoport(int servport) { return servport < 0 ? SAUERBRATEN_SERVINFO_PORT : servport+1; }
	int serverport(int infoport) { return infoport < 0 ? SAUERBRATEN_SERVER_PORT : infoport-1; }
	const char *defaultmaster() { return "sauerbraten.org"; }
	const char *defaultconfig() { return "server-init.cfg"; }
	int masterport() { return SAUERBRATEN_MASTER_PORT; }
	int numchannels() { return 3; }

	#include "extinfo.h"

	void serverinforeply(ucharbuf &req, ucharbuf &p)
	{
		if(!getint(req))
		{
			extserverinforeply(req, p);
			return;
		}

		putint(p, numclients(-1, false, true));
		putint(p, 5);				  // number of attrs following
		putint(p, PROTOCOL_VERSION);	// generic attributes, passed back below
		putint(p, gamemode);
		putint(p, max((gamelimit - gamemillis)/1000, 0));
		putint(p, getvar("capacity"));
		putint(p, serverprivate ? MM_PASSWORD : (mastermode || mastermask&MM_AUTOAPPROVE ? mastermode : MM_AUTH));
		sendstring(smapname, p);
		sendstring(serverdesc, p);
		sendserverinforeply(p);
	}

	bool servercompatible(char *name, char *sdec, char *map, int ping, const vector<int> &attr, int np)
	{
		return attr.length() && attr[0]==PROTOCOL_VERSION;
	}

	#include "aiman.h"
}

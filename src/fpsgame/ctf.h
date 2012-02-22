#ifndef PARSEMESSAGES

#define ctfteamflag(s) (!strcmp(s, "good") ? 1 : (!strcmp(s, "evil") ? 2 : 0))
#define ctfflagteam(i) (i==1 ? "good" : (i==2 ? "evil" : NULL))

struct ctfservmode : servmode
{
    static const int BASERADIUS = 64;
    static const int BASEHEIGHT = 24;
    static const int MAXFLAGS = 20;
    static const int FLAGRADIUS = 16;
    static const int FLAGLIMIT = 10;
    static const int MAXHOLDSPAWNS = 100;
    static const int HOLDSECS = 20;
    static const int HOLDFLAGS = 1;

    struct flag
    {
        int id, version, spawnindex;
        vec droploc, spawnloc;
        int team, droptime, owntime;
        int owner, dropper, invistime;

        flag() { reset(); }

        void reset()
        {
            version = 0;
            spawnindex = -1;
            droploc = spawnloc = vec(0, 0, 0);
            owner = dropper = -1;
            invistime = owntime = 0;
            team = 0;
            droptime = owntime = 0;
        }
    };

    struct holdspawn
    {
        vec o;
    };
    vector<holdspawn> holdspawns;
    vector<flag> flags;
    int scores[2];

    void resetflags()
    {
        holdspawns.shrink(0);
        flags.shrink(0);
        loopk(2) scores[k] = 0;
    }

    bool addflag(int i, const vec &o, int team, int invistime = 0)
    {
        if(i<0 || i>=MAXFLAGS) return false;
        while(flags.length()<=i) flags.add();
        flag &f = flags[i];
        f.reset();
        f.id = i;
        f.team = team;
        f.spawnloc = o;
        f.invistime = invistime;
        return true;
    }

    bool addholdspawn(const vec &o)
    {
        if(holdspawns.length() >= MAXHOLDSPAWNS) return false;
        holdspawn &h = holdspawns.add();
        h.o = o;
        return true;
    }

    void ownflag(int i, int owner, int owntime)
    {
        flag &f = flags[i];
        f.owner = owner;
        f.owntime = owntime;
        f.dropper = -1;
        f.invistime = 0;
    }

    void dropflag(int i, const vec &o, int droptime, int dropper = -1)
    {
        flag &f = flags[i];
        f.droploc = o;
        f.droptime = droptime;
        f.dropper = dropper;
        f.owner = -1;
        f.invistime = 0;
    }

    void returnflag(int i, int invistime = 0)
    {
        flag &f = flags[i];
        f.droptime = 0;
        f.owner = f.dropper = -1;
        f.invistime = invistime;
    }

    int totalscore(int team)
    {
        return team >= 1 && team <= 2 ? scores[team-1] : 0;
    }

    int setscore(int team, int score)
    {
        if(team >= 1 && team <= 2) return scores[team-1] = score;
        return 0;
    }

    int addscore(int team, int score)
    {
        if(team >= 1 && team <= 2) return scores[team-1] += score;
        return 0;
    }

    bool hidefrags() { return true; }

    int getteamscore(const char *team)
    {
        return totalscore(ctfteamflag(team));
    }

    void getteamscores(vector<teamscore> &tscores)
    {
        loopk(2) if(scores[k]) tscores.add(teamscore(ctfflagteam(k+1), scores[k]));
    }

    bool insidebase(const flag &f, const vec &o)
    {
        float dx = (f.spawnloc.x-o.x), dy = (f.spawnloc.y-o.y), dz = (f.spawnloc.z-o.z);
        return dx*dx + dy*dy <= BASERADIUS*BASERADIUS && fabs(dz) <= BASEHEIGHT;
    }

    static const int RESETFLAGTIME = 10000;
    static const int INVISFLAGTIME = 20000;

    bool notgotflags;

    ctfservmode() : notgotflags(false) {}

    void reset(bool empty)
    {
        resetflags();
        notgotflags = !empty;
    }

    void dropflag(clientinfo *ci)
    {
        if(notgotflags) return;
        if(ci->invisible) return;
        loopv(flags) if(flags[i].owner==ci->clientnum)
        {
            flag &f = flags[i];
            if(m_protect && insidebase(f, ci->state.o))
            {
                returnflag(i);
                SbPy::triggerEventIntInt("flag_replaced", ci->clientnum, i);
                sendf(-1, 1, "ri4", N_RETURNFLAG, ci->clientnum, i, ++f.version);
            }
            else
            {
                ivec o(vec(ci->state.o).mul(DMF));
                sendf(-1, 1, "ri7", N_DROPFLAG, ci->clientnum, i, ++f.version, o.x, o.y, o.z);
                SbPy::triggerEventIntInt("flag_dropped", ci->clientnum, i);
		ci->state.flags_droped++;
                dropflag(i, o.tovec().div(DMF), lastmillis, ci->clientnum);
            }
        }
    }

    void leavegame(clientinfo *ci, bool disconnecting = false)
    {
        dropflag(ci);
        loopv(flags) if(flags[i].dropper == ci->clientnum) flags[i].dropper = -1;
    }

    void died(clientinfo *ci, clientinfo *actor)
    {
        dropflag(ci);
        loopv(flags) if(flags[i].dropper == ci->clientnum)
        {
		flags[i].dropper = -1;
		if (actor != NULL) SbPy::triggerEventIntInt("flagger_stopped", ci->clientnum, actor->clientnum);
	}
    }

    bool canchangeteam(clientinfo *ci, const char *oldteam, const char *newteam)
    {
        return ctfteamflag(newteam) > 0;
    }

    void changeteam(clientinfo *ci, const char *oldteam, const char *newteam)
    {
        dropflag(ci);
    }

    void spawnflag(int i)
    {
        if(holdspawns.empty()) return;
        int spawnindex = flags[i].spawnindex;
        loopj(4)
        {
            spawnindex = rnd(holdspawns.length());
            if(spawnindex != flags[i].spawnindex) break;
        }
        flags[i].spawnindex = spawnindex;
        SbPy::triggerEventInt("flag_spawned", i);
    }

    void scoreflag(clientinfo *ci, int goal, int relay = -1)
    {
    	if(ci->invisible) return;
        returnflag(relay >= 0 ? relay : goal, m_protect ? lastmillis : 0);
        ci->state.flags++;
        int team = ctfteamflag(ci->team), score = addscore(team, 1);
        if(m_hold) spawnflag(goal);
        sendf(-1, 1, "rii9", N_SCOREFLAG, ci->clientnum, relay, relay >= 0 ? ++flags[relay].version : -1, goal, ++flags[goal].version, flags[goal].spawnindex, team, score, ci->state.flags);
	SbPy::triggerEventIntInt("flag_scored", ci->clientnum, relay);
        if(score >= FLAGLIMIT) startintermission();
    }

    void takeflag(clientinfo *ci, int i, int version)
    {
    	if(ci->invisible) return;
        if(notgotflags || !flags.inrange(i) || ci->state.state!=CS_ALIVE || !ci->team[0]) return;
        flag &f = flags[i];
        if((m_hold ? f.spawnindex < 0 : !ctfflagteam(f.team)) || f.owner>=0 || f.version != version || (f.droptime && f.dropper == ci->clientnum)) return;
        int team = ctfteamflag(ci->team);
        if(m_hold || m_protect == (f.team==team))
        {
            loopvj(flags) if(flags[j].owner==ci->clientnum) return;
            ownflag(i, ci->clientnum, lastmillis);
            sendf(-1, 1, "ri4", N_TAKEFLAG, ci->clientnum, i, ++f.version);
            SbPy::triggerEventIntInt("flag_taken", ci->clientnum, i);
        }
        else if(m_protect)
        {
            if(!f.invistime) scoreflag(ci, i);
        }
        else if(f.droptime)
        {
            returnflag(i);
            sendf(-1, 1, "ri4", N_RETURNFLAG, ci->clientnum, i, ++f.version);
        }
        else
        {
            loopvj(flags) if(flags[j].owner==ci->clientnum) { scoreflag(ci, i, j); break; }
        }
    }

    void update()
    {
        if(gamemillis>=gamelimit || notgotflags) return;
        loopv(flags)
        {
            flag &f = flags[i];
            if(f.owner<0 && f.droptime && lastmillis - f.droptime >= RESETFLAGTIME)
            {
                returnflag(i, m_protect ? lastmillis : 0);
                if(m_hold) spawnflag(i);
                sendf(-1, 1, "ri6", N_RESETFLAG, i, ++f.version, f.spawnindex, m_hold ? 0 : f.team, m_hold ? 0 : addscore(f.team, m_protect ? -1 : 0));
                SbPy::triggerEventInt("flag_reset", i);
            }
            if(f.invistime && lastmillis - f.invistime >= INVISFLAGTIME)
            {
                f.invistime = 0;
                sendf(-1, 1, "ri3", N_INVISFLAG, i, 0);
                SbPy::triggerEventInt("flag_solidified", i);
            }
            if(m_hold && f.owner>=0 && lastmillis - f.owntime >= HOLDSECS*1000)
            {
                clientinfo *ci = getinfo(f.owner);
                if(ci) scoreflag(ci, i);
                else
                {
                    spawnflag(i);
                    sendf(-1, 1, "ri6", N_RESETFLAG, i, ++f.version, f.spawnindex, 0, 0);
                    SbPy::triggerEventInt("flag_reset", i);
                }
            }
        }
    }

    void initclient(clientinfo *ci, packetbuf &p, bool connecting)
    {
        putint(p, N_INITFLAGS);
        loopk(2) putint(p, scores[k]);
        putint(p, flags.length());
        loopv(flags)
        {
            flag &f = flags[i];
            putint(p, f.version);
            putint(p, f.spawnindex);
            putint(p, f.owner);
            putint(p, f.invistime ? 1 : 0);
            if(f.owner<0)
            {
                putint(p, f.droptime ? 1 : 0);
                if(f.droptime)
                {
                    putint(p, int(f.droploc.x*DMF));
                    putint(p, int(f.droploc.y*DMF));
                    putint(p, int(f.droploc.z*DMF));
                }
            }
        }
    }

    void setServMapFlags(PyObject *args)
    {
    	int numflags;
    	int temp;
    	PyObject *tuple;
    	PyObject *tuple_flag;
    	PyArg_ParseTuple(args, "O", &tuple);

    	numflags = PyTuple_Size(tuple);

    	loopi(numflags)
    	{
    		tuple_flag = PyTuple_GetItem(tuple,i);

    		int team = PyInt_AsLong(PyTuple_GetItem(tuple_flag,0));
    		vec o;
    		loopk(3)
    		{
    			temp = PyInt_AsLong(PyTuple_GetItem(tuple_flag,k+1));
    			o[k] = max(temp/DMF, 0.0f);
    		}

    		if(m_hold) addholdspawn(o);
    		else addflag(i, o, team, m_protect ? lastmillis : 0);
    	}
    	if(m_hold)
    	{
    		if(holdspawns.length()) while(flags.length() < HOLDFLAGS)
    		{
    			int i = flags.length();
    			if(!addflag(i, vec(0, 0, 0), 0, 0)) break;
    			flag &f = flags[i];
    			spawnflag(i);
    			sendf(-1, 1, "ri6", N_RESETFLAG, i, ++f.version, f.spawnindex, 0, 0);

    		}
    	}
    	notgotflags = false;
    }

    void parseclientflags(clientinfo *ci, ucharbuf &p)
    {
        int numflags = getint(p);

    	std::vector<PyObject*> args;
    	PyObject *pCn = PyInt_FromLong(ci->clientnum);
    	PyObject *pTuple_flags = PyTuple_New(numflags);
    	PyObject *pTuple_flag;

        loopi(numflags)
        {
        	pTuple_flag = PyTuple_New(4);
            loopk(4)
            {
            	PyTuple_SetItem(pTuple_flag, k, PyInt_FromLong(getint(p)));
            }
            PyTuple_SetItem(pTuple_flags, i, pTuple_flag);
        }

    	args.push_back(pCn);
    	args.push_back(pTuple_flags);

        SbPy::triggerEvent("player_flag_list", &args);
    }

};


#elif SERVMODE

case N_TRYDROPFLAG:
{
    if((ci->state.state!=CS_SPECTATOR || ci->local || ci->privilege) && cq && smode==&ctfmode) ctfmode.dropflag(cq);
    break;
}

case N_TAKEFLAG:
{
    int flag = getint(p), version = getint(p);
    if((ci->state.state!=CS_SPECTATOR || ci->local || ci->privilege) && cq && smode==&ctfmode) ctfmode.takeflag(cq, flag, version);
    break;
}

case N_INITFLAGS:
    if(!(smode==&ctfmode))
    {
    	SbPy::triggerEventIntString("player_cheat", ci->clientnum, "Flag list in non-flag mode.");
    	int numflags = getint(p);
    	loopi(numflags){loopk(4){getint(p);}}
    	break;
    }
    ctfmode.parseclientflags(ci, p);
    break;
#endif


/*
 *   Copyright (C) 2009 Gregory Haynes <greg@greghaynes.net>
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; either version 2 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program; if not, write to the
 *   Free Software Foundation, Inc.,
 *   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
 */

#include "servermodule.h"
#include "server.h"

#include <iostream>

namespace SbPy
{

static PyObject *reinitializeHandlers(PyObject *self, PyObject *args)
{
	SbPy::reinitPy();
	return Py_None;
}

static PyObject *numClients(PyObject *self, PyObject *args)
{
	return Py_BuildValue("i", server::numclients());
}

static PyObject *clients(PyObject *self, PyObject *args)
{
	server::clientinfo *ci;
	std::vector<int> spects;
	std::vector<int>::iterator itr;
	PyObject *pTuple;
	PyObject *pInt;
	int y = 0;

	loopv(server::clients)
	{
		spects.push_back(i);
	}
	pTuple = PyTuple_New(spects.size());

	for(itr = spects.begin(); itr != spects.end(); itr++)
	{
		pInt = PyInt_FromLong(*itr);
		PyTuple_SetItem(pTuple, y, pInt);
		y++;
	}
	return pTuple;
}

static PyObject *players(PyObject *self, PyObject *args)
{
	server::clientinfo *ci;
	std::vector<int> spects;
	std::vector<int>::iterator itr;
	PyObject *pTuple;
	PyObject *pInt;
	int y = 0;
	
	loopv(server::clients)
	{
		ci = server::getinfo(i);
		if(ci && ci->state.state != CS_SPECTATOR)
			spects.push_back(i);
	}
	pTuple = PyTuple_New(spects.size());
	
	for(itr = spects.begin(); itr != spects.end(); itr++)
	{
		pInt = PyInt_FromLong(*itr);
		PyTuple_SetItem(pTuple, y, pInt);
		y++;
	}
	return pTuple;
}

static PyObject *spectators(PyObject *self, PyObject *args)
{
	server::clientinfo *ci;
	std::vector<int> spects;
	std::vector<int>::iterator itr;
	PyObject *pTuple;
	PyObject *pInt;
	int y = 0;
	
	loopv(server::clients)
	{
		ci = server::getinfo(i);
		if(ci && ci->state.state == CS_SPECTATOR)
		{
			spects.push_back(i);
		}
	}
	pTuple = PyTuple_New(spects.size());
	
	for(itr = spects.begin(); itr != spects.end(); itr++)
	{
		pInt = PyInt_FromLong(*itr);
		PyTuple_SetItem(pTuple, y, pInt);
		y++;
	}
	return pTuple;
}

static PyObject *message(PyObject *self, PyObject *args)
{
	PyObject *pMsg = PyTuple_GetItem(args, 0);
	if(pMsg)
	{
		char *msg = PyString_AsString(pMsg);
		if(msg)
			server::sendservmsg(msg);
	}
	else
		fprintf(stderr, "Error sending message");
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *playerMessage(PyObject *self, PyObject *args)
{
	int cn;
	char *text;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "is", &cn, &text))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	if(ci->state.aitype != AI_NONE)
	{
		PyErr_SetString(PyExc_ValueError, "Cannot send message to AI client");
		return 0;
	}
	sendf(cn, 1, "ris", N_SERVMSG, text);
	Py_INCREF(Py_None);
	return Py_None;
}

/* Never got the normal messages to work correctly
static PyObject *playerMessageTeam(PyObject *self, PyObject *args)
{
	int cn;
	char *text;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "is", &cn, &text))
		return 0;
	ci = server::getinfo(cn);
	
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	
	loopv(server::clients)
	{
		server::clientinfo *t = server::clients[i];
		if(t==ci || t->state.state==CS_SPECTATOR || t->state.aitype != AI_NONE || strcmp(ci->team, t->team)) continue;
		sendf(t->clientnum, 1, "riis", N_SAYTEAM, ci->clientnum, text);
	}
	
	Py_INCREF(Py_None);
	return Py_None;
}


static PyObject *playerMessageAll(PyObject *self, PyObject *args)
{
	int cn;
	char *text;
	int len;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "is", &cn, &text))
		return 0;
	ci = server::getinfo(cn);
	
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	
	//len = 0;
	len = strlen(text);
	
	sendf(-1, 1, "riiis", N_TEXT, ci->clientnum, len, text);
	
	//loopv(server::clients)
	//{
	//	server::clientinfo *t = server::clients[i];
	//	if(t==ci || t->state.state==CS_SPECTATOR || t->state.aitype != AI_NONE) continue;
	//	sendf(t->clientnum, 1, "riiis", N_TEXT, ci->clientnum, len, text);
	//}
	
	Py_INCREF(Py_None);
	return Py_None;
}
*/

static PyObject *playerName(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified.");
		return 0;
	}
	if(!ci->name)
	{
		PyErr_SetString(PyExc_RuntimeError, "Client cn is valid but has no name.");
		return 0;
	}
	return Py_BuildValue("s", ci->name);
}

static PyObject *playerSessionId(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	return Py_BuildValue("k", ci->sessionid);
}

static PyObject *playerIpLong(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	return Py_BuildValue("k", getclientip(ci->clientnum));
}

static PyObject *playerKick(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	disconnect_client(cn, DISC_KICK);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *playerDisc(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	disconnect_client(cn, DISC_NONE);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *playerPrivilege(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	return Py_BuildValue("i", ci->privilege);
}

static PyObject *requestPlayerAuth(PyObject *self, PyObject *args)
{
	int cn;
	char *desc;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "is", &cn, &desc))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	sendf(ci->clientnum, 1, "ris", N_REQAUTH, desc);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *playerFrags(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	return Py_BuildValue("i", ci->state.frags);
}

static PyObject *playerTeamkills(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	return Py_BuildValue("i", ci->state.teamkills);
}

static PyObject *playerDeaths(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	return Py_BuildValue("i", ci->state.deaths);
}

static PyObject *playerShots(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	return Py_BuildValue("i", ci->state.shots);
}

static PyObject *playerHits(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	return Py_BuildValue("i", ci->state.hits);
}

static PyObject *spectate(PyObject *self, PyObject *args)
{
	int spectator;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &spectator))
		return 0;
	ci = server::getinfo(spectator);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	server::spectate(ci, true, spectator);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *unspectate(PyObject *self, PyObject *args)
{
	int spectator;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &spectator))
		return 0;
	ci = server::getinfo(spectator);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	server::spectate(ci, false, spectator);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *setPlayerTeam(PyObject *self, PyObject *args)
{
	int cn;
	char *team;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "is", &cn, &team))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	server::setteam(ci, team);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *playerPing(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	return Py_BuildValue("i", ci->ping);
}

static PyObject *playerScore(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	return Py_BuildValue("i", ci->state.flags);
}

static PyObject *playerDamageDelt(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	return Py_BuildValue("i", ci->state.damage);
}

static PyObject *playerDamageRecieved(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	return Py_BuildValue("i", ci->state.damage_rec);
}

static PyObject *playerTeam(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	if(ci->state.state==CS_SPECTATOR)
	{
		PyErr_SetString(PyExc_ValueError, "Player is a spectator");
		return 0;
	}
	return Py_BuildValue("s", ci->team);
}

static PyObject *playerIsSpectator(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	return Py_BuildValue("b", ci->state.state == CS_SPECTATOR);
}

static PyObject *playerIsInvisible(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	return Py_BuildValue("b", ci->invisible);
}

static PyObject *setInvisible(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	ci->invisible = true;
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *setVisible(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	ci->invisible = false;
	Py_INCREF(Py_None);
	return Py_None;
}

// TODO: This should except on isufficient permissions
static PyObject *setBotLimit(PyObject *self, PyObject *args)
{
	int cn, limit;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "ii", &cn, &limit))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	if(!ci->local && ci->privilege < PRIV_ADMIN)
		sendf(cn, 1, "ris", N_SERVMSG, "Insufficient permissions to add bot.");
	else
		server::aiman::setbotlimit(ci, limit);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *hashPass(PyObject *self, PyObject *args)
{
	PyObject *pstr;
	int cn;
	char *pass;
	server::clientinfo *ci;
	string string;
	if(!PyArg_ParseTuple(args, "is", &cn, &pass))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	server::hashpassword(cn, ci->sessionid, pass, string, sizeof(string));
	pstr = PyString_FromString(string);
	return pstr;
}

static PyObject *genAuthKey(PyObject *self, PyObject *args)
{
	char *pass;
	PyObject *pstr;
	PyObject *pTuple = PyTuple_New(2);

	if(!PyArg_ParseTuple(args, "s", &pass))
		return 0;

	vector<char> pubkey, privkey;
	genprivkey(pass, privkey, pubkey);

	pstr = PyString_FromString(privkey.getbuf());
	PyTuple_SetItem(pTuple, 0, pstr);

	pstr = PyString_FromString(pubkey.getbuf());
	PyTuple_SetItem(pTuple, 1, pstr);

	return pTuple;
}

static PyObject *setMaster(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	if(cn != -1)
		ci = server::getinfo(cn);
	else
		ci = 0;
	if(cn != -1 && !ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	server::setcimaster(ci);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *setAdmin(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	server::setciadmin(ci);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *resetPrivilege(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	server::resetpriv(ci);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *setPaused(PyObject *self, PyObject *args)
{
	bool val;
	if(!PyArg_ParseTuple(args, "b", &val))
		return 0;
	server::pausegame(val);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *isPaused(PyObject *self, PyObject *args)
{
	return Py_BuildValue("b", server::gamepaused);
}

static PyObject *setMap(PyObject *self, PyObject *args)
{
	const char *map;
	int mode;
	if(!PyArg_ParseTuple(args, "si", &map, &mode))
		return 0;
	server::setmap(map, mode);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *setMasterMode(PyObject *self, PyObject *args)
{
	int mm;
	if(!PyArg_ParseTuple(args, "i", &mm))
		return 0;
	server::setmastermode(mm);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *setMasterMask(PyObject *self, PyObject *args)
{
	int mm;
	if(!PyArg_ParseTuple(args, "i", &mm))
		return 0;
	switch(mm)
	{
		case 1: server::mastermask = MM_PUBSERV; break;
		case 2: server::mastermask = MM_COOPSERV; break;
		case 3: server::mastermask = MM_AUTOAPPROVE; break;
		default:
			PyErr_SetString(PyExc_ValueError, "Invalid master mask.");
			return 0;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *masterMode(PyObject *self, PyObject *args)
{
	return Py_BuildValue("i", server::mastermode);
}

static PyObject *gameMode(PyObject *self, PyObject *args)
{
	return Py_BuildValue("i", server::gamemode);
}

static PyObject *mapName(PyObject *self, PyObject *args)
{
	return Py_BuildValue("s", server::smapname);
}

static PyObject *modeName(PyObject *self, PyObject *args)
{
	int mm;
	const char *name;
	if(!PyArg_ParseTuple(args, "i", &mm))
		return 0;
	if(!m_valid(mm))
	{
		PyErr_SetString(PyExc_ValueError, "Invalid mode");
		return 0;
	}
	name = server::modename(mm);
	return Py_BuildValue("s", name);
}

static PyObject *maxClients(PyObject *self, PyObject *args)
{
	return Py_BuildValue("i", maxclients);
}

static PyObject *setMaxClients(PyObject *self, PyObject *args)
{
	int mm;
	if(!PyArg_ParseTuple(args, "i", &mm))
		return 0;
	maxclients = mm;
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *uptime(PyObject *self, PyObject *args)
{
	return Py_BuildValue("i", totalmillis);
}

static PyObject *ip(PyObject *self, PyObject *args)
{
	if(*serverip)
		return Py_BuildValue("s", serverip);
	else
	{
		Py_INCREF(Py_None);
		return Py_None;
	}
}

static PyObject *port(PyObject *self, PyObject *args)
{
	if(serverport <= 0)
		return Py_BuildValue("i", server::serverport());
	else
		return Py_BuildValue("i", serverport);
}

static PyObject *authChal(PyObject *self, PyObject *args)
{
	int cn, id;
	char *chal;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "iis", &cn, &id, &chal))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	server::challengeauth(ci, id, chal);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *setGameMins(PyObject *self, PyObject *args)
{
	int mm;
	if(!PyArg_ParseTuple(args, "i", &mm))
		return 0;
	server::setgamemins(mm);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *adminPass(PyObject *self, PyObject *args)
{
	return Py_BuildValue("s", server::adminpass);
}

static PyObject *publicServer(PyObject *self, PyObject *args)
{
	return Py_BuildValue("i", server::publicserver);
}

static PyObject *setServerDesc(PyObject *self, PyObject *args)
{
	char *desc;
	if(!PyArg_ParseTuple(args, "s", &desc))
		return 0;


}

static PyObject *sendMapReload(PyObject *self, PyObject *args)
{
	server::sendmapreload();
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *serverPassword(PyObject *self, PyObject *args)
{
	return Py_BuildValue("s", server::serverpass);
}

static PyObject *minRemain(PyObject *self, PyObject *args)
{
	return Py_BuildValue("i", max((server::gamelimit - server::gamemillis)/1000, 0));
}

static PyObject *persistentIntermission(PyObject *self, PyObject *args)
{
	return Py_BuildValue("b", server::persistentIntermission);
}

static PyObject *setPersistentIntermission(PyObject *self, PyObject *args)
{
	bool val;
	if(!PyArg_ParseTuple(args, "b", &val))
		return 0;
	server::persistentIntermission = val;
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *allowShooting(PyObject *self, PyObject *args)
{
	return Py_BuildValue("b", server::allowShooting);
}

static PyObject *setAllowShooting(PyObject *self, PyObject *args)
{
	bool val;
	if(!PyArg_ParseTuple(args, "b", &val))
		return 0;
	server::allowShooting = val;
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *setTeam(PyObject *self, PyObject *args)
{
	int cn;
	char *team;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "is", &cn, &team))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	server::setteam(ci, team);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *pregameSetTeam(PyObject *self, PyObject *args)
{
	int cn;
	char *team;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "is", &cn, &team))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	server::pregame_setteam(ci, team);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *teamScore(PyObject *self, PyObject *args)
{
	char *team;
	if(!PyArg_ParseTuple(args, "s", &team))
		return 0;
	return Py_BuildValue("i", server::smode->getteamscore(team));
}

static PyObject *nextMatchRecorded(PyObject *self, PyObject *args)
{
	return Py_BuildValue("b", server::demonextmatch);
}

static PyObject *setRecordNextMatch(PyObject *self, PyObject *args)
{
	bool val;
	if(!PyArg_ParseTuple(args, "b", &val))
		return 0;
	server::demonextmatch = val;
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *demoSize(PyObject *self, PyObject *args)
{
	int num;
	if(!PyArg_ParseTuple(args, "i", &num))
		return 0;
	if(!server::demos.inrange(num))
	{
		PyErr_SetString(PyExc_ValueError, "Invalid demo number");
		return 0;
	}
	return Py_BuildValue("i", server::demos[num].len);
}

static PyObject *demoData(PyObject *self, PyObject *args)
{
	int num;
	if(!PyArg_ParseTuple(args, "i", &num))
		return 0;
	if(!server::demos.inrange(num))
	{
		PyErr_SetString(PyExc_ValueError, "Invalid demo number");
		return 0;
	}
	return Py_BuildValue("s", server::demos[num].data);
}

static PyObject *sendDemo(PyObject *self, PyObject *args)
{
	int cn, num;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "ii", &cn, &num))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}
	if(!server::demos.inrange(num))
	{
		PyErr_SetString(PyExc_ValueError, "Invalid demo number");
		return 0;
	}
	server::senddemo(cn, num);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *saveDemoFile(PyObject *self, PyObject *args)
{
	const char *path;
	if(!PyArg_ParseTuple(args, "s", &path))
		return 0;
	server::savedemofile(path);
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *suicide(PyObject *self, PyObject *args)
{
	int cn;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "i", &cn))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn");
		return 0;
	}
	server::suicide(ci);
	Py_INCREF(Py_None);
	return Py_None;
}

//static PyObject *configdir(PyObject *self, PyObject *args)
//{
//	return Py_BuildValue("s", server::pyconfigpath);
//}

static PyObject *instanceRoot(PyObject *self, PyObject *args)
{
	return Py_BuildValue("s", server::instanceRoot);
}

static PyObject *shutdown(PyObject *self, PyObject *args)
{
	int exit_status;
	if(!PyArg_ParseTuple(args, "i", &exit_status))
		return 0;

	exit(exit_status);
	return Py_None;
}

static PyMethodDef ModuleMethods[] = {
	{"reinitializeHandlers", reinitializeHandlers, METH_VARARGS, "Re-retreive python functions for the c++ handlers."},
	{"numClients", numClients, METH_VARARGS, "Return the number of clients on the server."},
	{"message", message, METH_VARARGS, "Send a server message."},
	{"clients", clients, METH_VARARGS, "List of client numbers."},
	{"players", players, METH_VARARGS, "List of client numbers of active clients."},
	{"spectators", spectators, METH_VARARGS, "List of client numbers of spectating clients."},
	{"playerMessage", playerMessage, METH_VARARGS, "Send a message to player."},
//	{"playerMessageAll", playerMessageAll, METH_VARARGS, "Broadcast a message as a player."},
//	{"playerMessageTeam", playerMessageTeam, METH_VARARGS, "Broadcast a team message as a player."},
	{"playerName", playerName, METH_VARARGS, "Get name of player from cn."},
	{"playerSessionId", playerSessionId, METH_VARARGS, "Session ID of player."},
	{"playerIpLong", playerIpLong, METH_VARARGS, "Get IP of player from cn."},
	{"playerKick", playerKick, METH_VARARGS, "Kick player from server."},
	{"playerDisc", playerDisc, METH_VARARGS, "Disconnect player from server."},
	{"playerPrivilege", playerPrivilege, METH_VARARGS, "Integer representing player privilege"},
	{"requestPlayerAuth", requestPlayerAuth, METH_VARARGS, "Request that a players client autoauth."},
	{"playerFrags", playerFrags, METH_VARARGS, "Number of frags by player in current match."},
	{"playerTeamkills", playerTeamkills, METH_VARARGS, "Number of teamkills by player in current match."},
	{"playerDeaths", playerDeaths, METH_VARARGS, "Number of deatds by player in current match."},
	{"playerShots", playerShots, METH_VARARGS, "Shots by player in current match."},
	{"playerHits", playerHits, METH_VARARGS, "Hits by player in current match."},
	{"playerPing", playerPing, METH_VARARGS, "Current ping of player."},
	{"playerScore", playerScore, METH_VARARGS, "Flags player has scored."},
	{"playerDamageDelt", playerDamageDelt, METH_VARARGS, "Damage delt by player in current game."},
	{"playerDamageRecieved", playerDamageRecieved, METH_VARARGS, "Damage recieved by player in current game."},
	{"playerTeam", playerTeam, METH_VARARGS, "Team player is member of."},
	{"playerIsSpectator", playerIsSpectator, METH_VARARGS, "Player is a spectator"},
	{"playerIsInvisible", playerIsInvisible, METH_VARARGS, "Player is invisible."},
	{"setInvisible", setInvisible, METH_VARARGS, "Set the player invisible."},
	{"setVisible", setVisible, METH_VARARGS, "Set the player visible."},
	{"spectate", spectate, METH_VARARGS, "Spectate player."},
	{"unspectate", unspectate, METH_VARARGS, "Set player to unspectated."},
	{"setPlayerTeam", setPlayerTeam, METH_VARARGS, "Set team of player."},
	{"setBotLimit", setBotLimit, METH_VARARGS, "Set server bot limit."},
	{"hashPassword", hashPass, METH_VARARGS, "Return hash for user + password"},
	{"genAuthKey", genAuthKey, METH_VARARGS, "Create auth key pair as a tuple (priv, pub)."},
	{"setMaster", setMaster, METH_VARARGS, "Set cn to master."},
	{"setAdmin", setAdmin, METH_VARARGS, "Set cn to admin."},
	{"resetPrivilege", resetPrivilege, METH_VARARGS, "Set cn to non-privileged."},
	{"setPaused", setPaused, METH_VARARGS, "Set game to be paused."},
	{"isPaused", isPaused, METH_VARARGS, "Is the game currently paused."},
	{"setMap", setMap, METH_VARARGS, "Set to map and mode."},
	{"setMasterMode", setMasterMode, METH_VARARGS, "Set server master mode."},
	{"masterMode", masterMode, METH_VARARGS, "Server master mode."},
	{"setMasterMask", setMasterMask, METH_VARARGS, "Set maximum master mode a master can set."},
	{"gameMode", gameMode, METH_VARARGS, "Current game mode."},
	{"mapName", mapName, METH_VARARGS, "Current map name."},
	{"modeName", modeName, METH_VARARGS, "Name of game mode."},
	{"maxClients", maxClients, METH_VARARGS, "Get current maximum number of allowed clients."},
	{"setMaxClients", setMaxClients, METH_VARARGS, "Set maximum number of allowed clients."},
	{"uptime", uptime, METH_VARARGS, "Number of milliseconds server has been running."},
	{"ip", ip, METH_VARARGS, "Current server ip."},
	{"port", port, METH_VARARGS, "Current server port."},
	{"authChallenge", authChal, METH_VARARGS, "Send auth challenge to client."},
	{"setMinsRemaining", setGameMins, METH_VARARGS, "Set the minutes remanining in current game."},
	{"adminPassword", adminPass, METH_VARARGS, "Get the administrator password."},
	{"publicServer", publicServer, METH_VARARGS, "Decides how masters are chosen and what privileges they have."},
	{"setServerDesc", setServerDesc, METH_VARARGS, "Set the server description."},
	{"sendMapReload", sendMapReload, METH_VARARGS, "Causes all users to send vote on next map."},
	{"serverPassword", serverPassword, METH_VARARGS, "Password for entry to the server."},
	{"minutesRemaining", minRemain, METH_VARARGS, "Minutes remaining in current match."},
	{"persistentIntermission", persistentIntermission, METH_VARARGS, "Get whether or not persistent intermission is enabled."},
	{"setPersistentIntermission", setPersistentIntermission, METH_VARARGS, "Set whether or not persistent intermission is enabled."},
	{"allowShooting", allowShooting, METH_VARARGS, "get whether or not shooting is allowed."},
	{"setAllowShooting", setAllowShooting, METH_VARARGS, "set whether or not shooting is allowed."},
	{"setTeam", setTeam, METH_VARARGS, "Set team of player."},
	{"pregameSetTeam", pregameSetTeam, METH_VARARGS, "Set team of player as a result of autoteam event."},
	{"teamScore", teamScore, METH_VARARGS, "Score of team."},
	{"nextMatchRecorded", nextMatchRecorded, METH_VARARGS, "Is next match being recorded."},
	{"setRecordNextMatch", setRecordNextMatch, METH_VARARGS, "Set to record demo of next match."},
	{"demoSize", demoSize, METH_VARARGS, "Size of demo in bytes."},
	{"demoData", demoData, METH_VARARGS, "Demo data."},
	{"sendDemo", sendDemo, METH_VARARGS, "Send demo to client."},
	{"saveDemoFile", saveDemoFile, METH_VARARGS, "Save last demo file."},
	{"suicide", suicide, METH_VARARGS, "Force client to commit suicide."},
//	{"configdir", configdir, METH_VARARGS, "Python config dir."},
	{"instanceRoot", instanceRoot, METH_VARARGS, "Get the root directory of the instance."},
	{"shutdown", shutdown, METH_VARARGS, "Shutdown the c++ side of things."},
	{NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initModule(void)
{
	(void) Py_InitModule("sbserver", ModuleMethods);
	return;
}


}

/*
 *   Copyright (C) 2012 Morgan Borman <morgan.borman@gmail.com>
 *
 *   This is a derivative work as permitted under the GPL license.
 *   Which included the following copyright notice;
 *
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
#include "tools.h"

#include <iostream>

int intlen(int val)
{
	if (val < 128 && val > -127) { return 1; }
	else if(val < 0x8000 && val >= -0x8000) { return 2; }
	else { return 4; }
}

namespace SbPy
{
	static PyObject *clientName(PyObject *self, PyObject *args)
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

	static PyObject *clientConnectPassword(PyObject *self, PyObject *args)
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
		if(!ci->connectpwd)
		{
			PyErr_SetString(PyExc_RuntimeError, "Client cn is valid but has no connectpwd.");
			return 0;
		}
		return Py_BuildValue("s", ci->connectpwd);
	}

	static PyObject *clientSessionId(PyObject *self, PyObject *args)
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

	static PyObject *clientIpLong(PyObject *self, PyObject *args)
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

	static PyObject *clientPrivilege(PyObject *self, PyObject *args)
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

	static PyObject *clientPing(PyObject *self, PyObject *args)
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

	static PyObject *clientTeam(PyObject *self, PyObject *args)
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
		return Py_BuildValue("s", ci->team);
	}

	static PyObject *clientState(PyObject *self, PyObject *args)
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
		return Py_BuildValue("i", ci->state.state);
	}

	static PyObject *clientMapCrc(PyObject *self, PyObject *args)
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
		return Py_BuildValue("i", ci->mapcrc);
	}

	static PyObject *clientMapName(PyObject *self, PyObject *args)
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
		return Py_BuildValue("s", ci->clientmap);
	}

	static PyObject *clientFrags(PyObject *self, PyObject *args)
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

	static PyObject *clientDeaths(PyObject *self, PyObject *args)
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

	static PyObject *clientTeamkills(PyObject *self, PyObject *args)
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

	static PyObject *clientShots(PyObject *self, PyObject *args)
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

	static PyObject *clientHits(PyObject *self, PyObject *args)
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

	static PyObject *clientScore(PyObject *self, PyObject *args)
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

	static PyObject *clientDamageDealt(PyObject *self, PyObject *args)
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

	static PyObject *clientDamageRecieved(PyObject *self, PyObject *args)
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

	static PyObject *clientDisconnect(PyObject *self, PyObject *args)
	{
		int cn;
		int reason;
		server::clientinfo *ci;
		if(!PyArg_ParseTuple(args, "ii", &cn, &reason))
			return 0;
		ci = server::getinfo(cn);
		if(!ci)
		{
			PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
			return 0;
		}
		//enum { DISC_NONE = 0, DISC_EOP, DISC_CN, DISC_KICK, DISC_TAGT, DISC_IPBAN, DISC_PRIVATE, DISC_MAXCLIENTS, DISC_TIMEOUT, DISC_OVERFLOW, DISC_NUM };
		if (reason < DISC_NONE || reason > DISC_NUM)
		{
			PyErr_SetString(PyExc_ValueError, "That is not a valid disconnect reason.");
			return 0;
		}
		disconnect_client(cn, reason);
		Py_INCREF(Py_None);
		return Py_None;
	}
	
	static PyObject *clientSetDisconnect(PyObject *self, PyObject *args)
	{
		int cn;
		int reason;
		server::clientinfo *ci;
		if(!PyArg_ParseTuple(args, "ii", &cn, &reason))
			return 0;
		ci = server::getinfo(cn);
		if(!ci)
		{
			PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
			return 0;
		}
		//enum { DISC_NONE = 0, DISC_EOP, DISC_CN, DISC_KICK, DISC_TAGT, DISC_IPBAN, DISC_PRIVATE, DISC_MAXCLIENTS, DISC_TIMEOUT, DISC_OVERFLOW, DISC_NUM };
		if (reason < DISC_NONE || reason > DISC_NUM)
		{
			PyErr_SetString(PyExc_ValueError, "That is not a valid disconnect reason.");
			return 0;
		}
		ci->disconnect_reason = reason;
		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *clientInitialize(PyObject *self, PyObject *args)
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
		if(ci->state.aitype != AI_NONE)
		{
			PyErr_SetString(PyExc_ValueError, "Cannot send client init to AI client");
			return 0;
		}
		server::sendClientInitialization(ci);
		Py_INCREF(Py_None);
		return Py_None;
	}
	
	static PyObject *clientMessage(PyObject *self, PyObject *args)
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
	
	static PyObject *clientMessageAll(PyObject *self, PyObject *args)
	{
		int cn;
		int tcn;
		char *text;
		server::clientinfo *ci;
		server::clientinfo *tci;
		if(!PyArg_ParseTuple(args, "iis", &cn, &tcn, &text))
			return 0;
		ci = server::getinfo(cn);
		tci = server::getinfo(tcn);

		if(!ci)
		{
			PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
			return 0;
		}

		if(!tci)
		{
			PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
			return 0;
		}

		sendf(tci->clientnum, 1, "riiiis", N_CLIENT, ci->clientnum, strlen(text)+2, N_TEXT, text);

		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *clientMessageTeam(PyObject *self, PyObject *args)
	{
		int cn;
		int tcn;
		char *text;
		server::clientinfo *ci;
		server::clientinfo *tci;
		if(!PyArg_ParseTuple(args, "iis", &cn, &tcn, &text))
			return 0;
		ci = server::getinfo(cn);
		tci = server::getinfo(tcn);

		if(!ci)
		{
			PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
			return 0;
		}

		if(!tci)
		{
			PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
			return 0;
		}

		sendf(tci->clientnum, 1, "riis", N_SAYTEAM, ci->clientnum, text);

		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *clientSendMap(PyObject *self, PyObject *args)
	{
		int cn;
		uchar *data;
		int len;
		server::clientinfo *ci;
		if(!PyArg_ParseTuple(args, "is#", &cn, &data, &len))
			return 0;
		ci = server::getinfo(cn);
		if(!ci)
		{
			PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
			return 0;
		}
		if(ci->state.aitype != AI_NONE)
		{
			PyErr_SetString(PyExc_ValueError, "Cannot send map to AI client");
			return 0;
		}

		//uchar *data;

		//memcpy (data,cdata,len);

		//char *tempfilename;
		defformatstring(tempfilename)("sendmap_%d", lastmillis);

		stream *datafile = opentempfile(tempfilename, "w+b");
	    if(!datafile) { sendf(cn, 1, "ris", N_SERVMSG, "failed to open temporary file when preparing to send"); return Py_None; }
	    datafile->write(data, len);

		sendfile(cn, 2, datafile, "ri", N_SENDMAP);

		if(datafile) DELETEP(datafile);
		return Py_None;
	}

	static PyObject *clientRequestAuth(PyObject *self, PyObject *args)
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

	static PyObject *clientChallengeAuth(PyObject *self, PyObject *args)
	{
		int cn, id;
		char *domain, *chal;
		server::clientinfo *ci;
		if(!PyArg_ParseTuple(args, "iiss", &cn, &id, &domain, &chal))
			return 0;
		ci = server::getinfo(cn);
		if(!ci)
		{
			PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
			return 0;
		}
		server::challengeauth(ci, id, domain, chal);
		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *clientSendDemo(PyObject *self, PyObject *args)
	{
		int cn, len;
		uchar *data;
		server::clientinfo *ci;
		if(!PyArg_ParseTuple(args, "is#", &cn, data, &len))
			return 0;
		ci = server::getinfo(cn);
		if(!ci)
		{
			PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
			return 0;
		}
	    sendf(cn, 2, "rim", N_SENDDEMO, len, data);
		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *clientSetVariable(PyObject *self, PyObject *args)
	{
		int cn;
		int tcn;
		int msglen = 0;
		server::clientinfo *ci;
		server::clientinfo *tci;
		char *variableName;
		int value;
		if(!PyArg_ParseTuple(args, "iisi", &cn, &tcn, &variableName, &value)) return 0;

		ci = server::getinfo(cn);
		if(!ci)
		{
			PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
			return 0;
		}
		if(ci->state.aitype != AI_NONE)
		{
			PyErr_SetString(PyExc_ValueError, "Cannot send message from AI client");
			return 0;
		}

		tci = server::getinfo(tcn);
		if(!tci)
		{
			PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
			return 0;
		}
		if(tci->state.aitype != AI_NONE)
		{
			PyErr_SetString(PyExc_ValueError, "Cannot send message to AI client");
			return 0;
		}

		msglen = 2+strlen(variableName)+2+intlen(value);


	    sendf(tcn, 1, "riiiiisi", N_CLIENT, cn, msglen, N_EDITVAR, ID_VAR, variableName, value);

		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *clientSetPrivilege(PyObject *self, PyObject *args)
	{
		int cn, level;
		server::clientinfo *ci;
		if(!PyArg_ParseTuple(args, "ii", &cn, &level))
			return 0;
		ci = server::getinfo(cn);
		if(!ci)
		{
			PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
			return 0;
		}
		server::setprivilege(ci, level);
		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *clientSetTeam(PyObject *self, PyObject *args)
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

	static PyObject *clientPregameSetTeam(PyObject *self, PyObject *args)
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

	static PyObject *clientSetSpectator(PyObject *self, PyObject *args)
	{
		int cn, val;
		server::clientinfo *ci;
		if(!PyArg_ParseTuple(args, "ii", &cn, &val))
			return 0;
		ci = server::getinfo(cn);
		if(!ci)
		{
			PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
			return 0;
		}
		server::spectate(ci, val);
		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *clientSetInvisible(PyObject *self, PyObject *args)
	{
		int cn, val;
		server::clientinfo *ci;
		if(!PyArg_ParseTuple(args, "ii", &cn, &val))
			return 0;
		ci = server::getinfo(cn);
		if(!ci)
		{
			PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
			return 0;
		}
		server::setinvisible(ci, val);
		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *clientSuicide(PyObject *self, PyObject *args)
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

	static PyObject *clienthashPassword(PyObject *self, PyObject *args)
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

	static PyObject *serverClientCount(PyObject *self, PyObject *args)
	{
		return Py_BuildValue("i", server::numclients());
	}

	static PyObject *serverClients(PyObject *self, PyObject *args)
	{
		server::clientinfo *ci;
		std::vector<int> clients;
		std::vector<int>::iterator itr;
		PyObject *pTuple;
		PyObject *pInt;
		int y = 0;

		loopv(server::clients)
		{
			clients.push_back(i);
		}
		pTuple = PyTuple_New(clients.size());

		for(itr = clients.begin(); itr != clients.end(); itr++)
		{
			pInt = PyInt_FromLong(*itr);
			PyTuple_SetItem(pTuple, y, pInt);
			y++;
		}
		return pTuple;
	}

	static PyObject *serverClientStates(PyObject *self, PyObject *args)
	{
		server::clientinfo *ci;
		PyObject *pClientStates = PyDict_New();

		loopv(server::clients)
		{
			ci = server::getinfo(i);
			if(ci)
			{
				PyDict_SetItem(pClientStates, PyInt_FromLong(ci->clientnum), PyInt_FromLong(ci->state.state));
			}
		}
		return pClientStates;
	}

	static PyObject *serverUptime(PyObject *self, PyObject *args)
	{
		return Py_BuildValue("i", totalmillis);
	}

	static PyObject *serverTimeRemaining(PyObject *self, PyObject *args)
	{
		return Py_BuildValue("i", max((server::gamelimit - server::gamemillis)/1000, 0));
	}

	static PyObject *serverGetVariable(PyObject *self, PyObject *args)
	{
	    char *variableName;
	    if(!PyArg_ParseTuple(args, "s", &variableName))
	    	return 0;

	    ident *id = idents->access(variableName);
	    if(id)
	    {
	        switch(id->type)
	        {
				case ID_VAR:
				{
					return Py_BuildValue("i", *id->storage.i);
					break;
				}
				case ID_FVAR:
				{
					return Py_BuildValue("f", *id->storage.f);
					break;
				}
				case ID_SVAR:
				{
					return Py_BuildValue("s", *id->storage.s);
					break;
				}
				default:
				{
					PyErr_SetString(PyExc_ValueError, "Invalid variable specified");
					return 0;
				}
	        }
	    }
		else
		{
			PyErr_SetString(PyExc_ValueError, "Invalid variable specified");
			return 0;
		}
	}

	static PyObject *serverPaused(PyObject *self, PyObject *args)
	{
		return Py_BuildValue("b", server::gamepaused);
	}

	static PyObject *serverMasterMode(PyObject *self, PyObject *args)
	{
		return Py_BuildValue("i", server::mastermode);
	}

	static PyObject *serverMasterMask(PyObject *self, PyObject *args)
	{
		return Py_BuildValue("i", server::mastermask);
	}

	static PyObject *serverGameMode(PyObject *self, PyObject *args)
	{
		return Py_BuildValue("i", server::gamemode);
	}

	static PyObject *serverMapName(PyObject *self, PyObject *args)
	{
		return Py_BuildValue("s", server::smapname);
	}

	static PyObject *serverMaxClients(PyObject *self, PyObject *args)
	{
		return Py_BuildValue("i", maxclients);
	}

	static PyObject *serverCapacity(PyObject *self, PyObject *args)
	{
		return Py_BuildValue("i", server::capacity);
	}

	static PyObject *serverTeamScore(PyObject *self, PyObject *args)
	{
		char *team;
		if(!PyArg_ParseTuple(args, "s", &team))
			return 0;
		return Py_BuildValue("i", server::smode->getteamscore(team));
	}

	static PyObject *serverMatchRecording(PyObject *self, PyObject *args)
	{
		return Py_BuildValue("b", (bool)server::demorecord);
	}

	static PyObject *serverNextMatchRecording(PyObject *self, PyObject *args)
	{
		return Py_BuildValue("b", server::demonextmatch || server::persistentdemos);
	}

	static PyObject *serverInstanceRoot(PyObject *self, PyObject *args)
	{
		return Py_BuildValue("s", server::instanceRoot);
	}

	static PyObject *serverReload(PyObject *self, PyObject *args)
	{
		SbPy::reload_on_update = true;
		return Py_None;
	}

	static PyObject *serverSetVariable(PyObject *self, PyObject *args)
	{
	    char *variableName;
	    char *value;
	    if(!PyArg_ParseTuple(args, "ss", &variableName, &value))
	    	return 0;
	    static string scmdval; scmdval[0] = 0;
	    ident *id = idents->access(variableName);
	    if(id)
	    {
	        switch(id->type)
	        {
				case ID_VAR:
				{
	                int ret = parseint(value);
	                if(ret < id->minval || ret > id->maxval)
	                {
	                	PyErr_Format(PyExc_ValueError,
	                        id->flags&IDF_HEX ?
	                                (id->minval <= 255 ? "valid range for %s is %d..0x%X" : "valid range for %s is 0x%X..0x%X") :
	                                "valid range for %s is %d..%d", variableName, id->minval, id->maxval);
	                    return 0;
	                }
	                setvar(variableName, ret);
					break;
				}
				case ID_FVAR:
				{
	                float ret = parsefloat(value);
	                if(ret < id->minvalf || ret > id->maxvalf)
	                {
	                	PyErr_Format(PyExc_ValueError, "valid range for %s is %s..%s", variableName, floatstr(id->minvalf), floatstr(id->maxvalf));
	                    return 0;
	                }
	                setfvar(variableName, ret);
	                break;
				}
				case ID_SVAR:
				{
	                setsvar(variableName, value);
					break;
				}
				default:
				{
					PyErr_SetString(PyExc_ValueError, "Unknown server variable type");
					return 0;
					break;
				}
	        }
	        printf("hopefully to set: %s to %s\n", variableName, value);
	    	Py_INCREF(Py_None);
	    	return Py_None;
	    }
		PyErr_SetString(PyExc_ValueError, "Invalid variable specified");
		return 0;
	}

	static PyObject *serverMessage(PyObject *self, PyObject *args)
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

	static PyObject *serverSetBotLimit(PyObject *self, PyObject *args)
	{
		int limit;
		if(!PyArg_ParseTuple(args, "i", &limit))
			return 0;
		if (limit < 128 && limit >= 0)
		{
			server::aiman::setbotlimit(limit);
		}
		else
		{
			PyErr_SetString(PyExc_ValueError, "Valid range for bot limit is 0<=i<=127 ");
			return 0;
		}
		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *serverSetBotBalance(PyObject *self, PyObject *args)
	{
		bool val;
		if(!PyArg_ParseTuple(args, "b", &val))
			return 0;
		server::aiman::setbotbalance(val);
		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *serverSetPaused(PyObject *self, PyObject *args)
	{
		bool val;
		if(!PyArg_ParseTuple(args, "b", &val))
			return 0;
		server::pausegame(val);
		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *serverSendMapReload(PyObject *self, PyObject *args)
	{
		server::sendmapreload();
		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *serverSetMapMode(PyObject *self, PyObject *args)
	{
		const char *map;
		int mode;
		if(!PyArg_ParseTuple(args, "si", &map, &mode))
			return 0;
		server::setmap(map, mode);
		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *serverSetMapItems(PyObject *self, PyObject *args)
	{
		if (!server::is_item_mode())
		{
			PyErr_SetString(PyExc_StandardError, "Can only set items during item modes.");
			return 0;
		}

		server::setServMapItems(args);

		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *serverSetMapFlags(PyObject *self, PyObject *args)
	{
		return server::setServMapFlags(args);
	}

	static PyObject *serverSetMapBases(PyObject *self, PyObject *args)
	{
		return server::setServMapBases(args);
	}

	static PyObject *serverSetCapacity(PyObject *self, PyObject *args)
	{
		int capacity;
		if(!PyArg_ParseTuple(args, "i", &server::capacity))
			return 0;
		setvar("capacity", capacity);
		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *serverSetMasterMode(PyObject *self, PyObject *args)
	{
		int mm;
		if(!PyArg_ParseTuple(args, "i", &mm))
			return 0;
		server::setmastermode(mm);
		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *serverSetMasterMask(PyObject *self, PyObject *args)
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

	static PyObject *serverSetRecordNextMatch(PyObject *self, PyObject *args)
	{
		bool val;
		if(!PyArg_ParseTuple(args, "b", &val))
			return 0;
		server::demonextmatch = val;
		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *serverSetTimeRemaining(PyObject *self, PyObject *args)
	{
		int milliseconds;
		if(!PyArg_ParseTuple(args, "i", &milliseconds))
			return 0;
		server::setTimeLeft(milliseconds);
		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *serverStartIntermission(PyObject *self, PyObject *args)
	{
		server::startintermission();
		Py_INCREF(Py_None);
		return Py_None;
	}

	static PyObject *serverShutdown(PyObject *self, PyObject *args)
	{
		int exit_status;
		if(!PyArg_ParseTuple(args, "i", &exit_status))
			return 0;

		exit(exit_status);
		return Py_None;
	}

	static PyObject *generateAuthKey(PyObject *self, PyObject *args)
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

	static PyObject *generateAuthChallenge(PyObject *self, PyObject *args)
	{
		//publicKey
		char *publicKey;
		if(!PyArg_ParseTuple(args, "s", &publicKey))
			return 0;

		uint seed[3] = { randomMT(), randomMT(), randomMT() };
		vector<char> challengeBuf;
		vector<char> answerBuf;
		void *parsedKey = parsepubkey(publicKey);
		genchallengestr(parsedKey, seed, sizeof(seed), challengeBuf, answerBuf);

		freepubkey(parsedKey);

		return Py_BuildValue("(ss)", challengeBuf.getbuf(), answerBuf.getbuf());
	}

#define def(NAME, DOC)  {#NAME, NAME, METH_VARARGS, DOC}

static PyMethodDef ModuleMethods[] = {

	def(clientName, 				"Get client name."),
	def(clientConnectPassword, 		"Get client connect password."),
	def(clientSessionId, 			"Get client Session ID of client."),
	def(clientIpLong, 				"Get client IP."),
	def(clientPrivilege, 			"Get client advertised privilege."),
	def(clientPing, 				"Get client ping."),
	def(clientTeam, 				"Get client team name."),
	def(clientState, 				"Get client state."),
	def(clientMapCrc, 				"Get client map crc."),
	def(clientMapName, 				"Get client map name."),

	def(clientFrags, 				"Get client frags in current match."),
	def(clientDeaths, 				"Get client deaths in current match."),
	def(clientTeamkills, 			"Get client teamkills in current match."),
	def(clientShots, 				"Get client shots in current match."),
	def(clientHits, 				"Get client hits in current match."),
	def(clientScore, 				"Get client flags scored in current match."),
	def(clientDamageDealt, 			"Get client total damage dealt in current match."),
	def(clientDamageRecieved, 		"Get client total damage received in current match."),

	def(clientDisconnect, 			"Disconnect client from server for a specific reason."),
	def(clientSetDisconnect, 		"Set the client to be disconnected on next server slice for a specific reason."),
	def(clientInitialize, 			"Send map initialization and item lists to client."),
	def(clientMessage, 				"Send a message to client."),
	def(clientMessageAll, 			"Send a message as one client to another(from, to, text)."),
	def(clientMessageTeam, 			"Send a team message as one client to another(from, to, text)."),
	def(clientSendMap, 				"Send the edit map to the client."),
	def(clientRequestAuth, 			"send request for client to auto-auth."),
	def(clientChallengeAuth, 		"Send auth challenge to client."),
	def(clientSendDemo, 			"Send demo to client."),
	def(clientSetVariable, 			"Set a client variable."),
	def(clientSetPrivilege, 		"Set client advertised privilege."),
	def(clientSetTeam, 				"Set team of client."),
	def(clientPregameSetTeam, 		"Set team of player as a result of autoteam event."),
	def(clientSetSpectator, 		"Set the spectator state of the client."),
	def(clientSetInvisible, 		"Set the invisible state of the client."),
	def(clientSuicide,				"Cause the client to suicide."),
	def(clienthashPassword, 		"Return hash for user + password"),

	def(serverClientCount, 			"Return the number of clients on the server."),
	def(serverClients, 				"Tuple of client numbers."),
	def(serverClientStates, 		"Dictionary of client states indexed by cn."),
	def(serverUptime, 				"Get the uptime in milliseconds."),
	def(serverTimeRemaining, 		"Get the remaining match time in milliseconds."),
	def(serverGetVariable, 			"Get a server variable."),
	def(serverPaused, 				"Get the paused state."),
	def(serverMasterMode, 			"Get the master mode."),
	def(serverMasterMask, 			"Get the master mask."),
	def(serverGameMode, 			"Get the game mode."),
	def(serverMapName, 				"Get the map name."),
	def(serverMaxClients, 			"Get the maximum clients which can be connected."),
	def(serverCapacity, 			"Get the advertised server capacity."),
	def(serverTeamScore, 			"Get the score of a team by name."),
	def(serverMatchRecording, 		"Get whether or not this match is being recorded."),
	def(serverNextMatchRecording, 	"Get whether or not the next match will be recorded."),
	def(serverInstanceRoot, 		"Get the root directory of the instance."),

	def(serverReload, 				"Stop and restart the python interpreter then reload all python systems."),
	def(serverSetVariable, 			"Set a server variable."),
	def(serverMessage, 				"Send a server message."),
	def(serverSetBotLimit, 			"Set the bot limit."),
	def(serverSetBotBalance, 		"Set the bot balance."),
	def(serverSetPaused, 			"Set the game paused state."),
	def(serverSendMapReload, 		"Send map reload request to all clients."),
	def(serverSetMapMode, 			"Set server map and mode."),
	def(serverSetMapItems, 			"Populate the servers entity spawn tracking data."),
	def(serverSetMapFlags, 			"Populate the servers flag spawn tracking data for flag modes."),
	def(serverSetMapBases, 			"Populate the servers base spawn tracking data for capture modes."),
	def(serverSetCapacity, 			"Set advertised max number of clients."),
	def(serverSetMasterMode, 		"Set server master mode."),
	def(serverSetMasterMask, 		"Set maximum master mode a master can set."),
	def(serverSetRecordNextMatch,	"Set the server to record the next match."),
	def(serverSetTimeRemaining, 	"Set the number of seconds remaining in current game in milliseconds."),
	def(serverStartIntermission, 	"Set the current game state to intermission."),
	def(serverShutdown, 			"Shutdown the c++ side of things."),

	def(generateAuthKey, 			"Create and return an auth key pair as a tuple (private, public)."),
	def(generateAuthChallenge, 		"given (cn, serverDesc, id, pubkey) sends challenge to client and returns correct answer."),

	{NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initModule(void)
{
	(void) Py_InitModule("sbserver", ModuleMethods);
	return;
}


}

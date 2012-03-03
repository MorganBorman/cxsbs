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

static PyObject *reload(PyObject *self, PyObject *args)
{
	SbPy::reload_on_update = true;
	return Py_None;
}

static PyObject *getVariable(PyObject *self, PyObject *args)
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

static PyObject *setVariable(PyObject *self, PyObject *args)
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

static PyObject *setClientVariable(PyObject *self, PyObject *args)
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

static PyObject *sendClientInitialization(PyObject *self, PyObject *args)
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
	return Py_None;
}

static PyObject *sendEditMap(PyObject *self, PyObject *args)
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

static PyObject *playerMessageTeam(PyObject *self, PyObject *args)
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

static PyObject *playerMessageAll(PyObject *self, PyObject *args)
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

static PyObject *playerConnectPwd(PyObject *self, PyObject *args)
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
	//if(!ci->connectpwd)
	if(!ci->name)
	{
		PyErr_SetString(PyExc_RuntimeError, "Client cn is valid but has no connectpwd.");
		return 0;
	}
	//return Py_BuildValue("s", ci->connectpwd);
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

static PyObject *playerMapCrc(PyObject *self, PyObject *args)
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

static PyObject *playerMapName(PyObject *self, PyObject *args)
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

static PyObject *playerDisconnect(PyObject *self, PyObject *args)
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

static PyObject *sendAuthChallenge(PyObject *self, PyObject *args)
{
	//cn, domain, reqid, publicKey
	//return answer to challenge
	int cn;
	char *domain;
	uint id;
	char *publicKey;
	server::clientinfo *ci;
	if(!PyArg_ParseTuple(args, "isIs", &cn, &domain, &id, &publicKey))
		return 0;
	ci = server::getinfo(cn);
	if(!ci)
	{
		PyErr_SetString(PyExc_ValueError, "Invalid cn specified");
		return 0;
	}

    uint seed[3] = { randomMT(), randomMT(), randomMT() };
    vector<char> challengeBuf;
    vector<char> answerBuf;
    void *parsedKey = parsepubkey(publicKey);
    genchallengestr(parsedKey, seed, sizeof(seed), challengeBuf, answerBuf);

    freepubkey(parsedKey);
    sendf(ci->clientnum, 1, "risis", N_AUTHCHAL, domain, id, challengeBuf.getbuf());

    return Py_BuildValue("s", answerBuf.getbuf());
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

static PyObject *setStateDead(PyObject *self, PyObject *args)
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
	ci->state.state = CS_DEAD;
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

static PyObject *playerDamageDealt(PyObject *self, PyObject *args)
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
	//if(ci->state.state==CS_SPECTATOR)
	//{
	//	PyErr_SetString(PyExc_ValueError, "Player is a spectator");
	//	return 0;
	//}
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

static PyObject *setMapItems(PyObject *self, PyObject *args)
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

static PyObject *setMapFlags(PyObject *self, PyObject *args)
{
	return server::setServMapFlags(args);
}

static PyObject *setMapBases(PyObject *self, PyObject *args)
{
	return server::setServMapBases(args);
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
	setvar("maxclients", mm);
	//maxclients = mm;
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *uptime(PyObject *self, PyObject *args)
{
	return Py_BuildValue("i", totalmillis);
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

static PyObject *setSecondsLeft(PyObject *self, PyObject *args)
{
	int seconds;
	if(!PyArg_ParseTuple(args, "i", &seconds))
		return 0;
	server::setSecondsLeft(seconds);
	Py_INCREF(Py_None);
	return Py_None;
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

static PyObject *secondsLeft(PyObject *self, PyObject *args)
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
	{"reload", reload, METH_VARARGS, "Re-retreive python functions for the c++ handlers."},

	{"getVariable", getVariable, METH_VARARGS, "Get a server variable."},
	{"setVariable", setVariable, METH_VARARGS, "Set a server variable."},

	{"setClientVariable", setClientVariable, METH_VARARGS, "Set a clients variables."},

	{"numClients", numClients, METH_VARARGS, "Return the number of clients on the server."},

	{"message", message, METH_VARARGS, "Send a server message."},

	{"sendClientInitialization", sendClientInitialization, METH_VARARGS, "Send the initial map change and items list to the client after they have connected."},

	{"sendEditMap", sendEditMap, METH_VARARGS, "Send the initial map change and items list to the client after they have connected."},

	{"clients", clients, METH_VARARGS, "List of client numbers."},
	{"players", players, METH_VARARGS, "List of client numbers of active clients."},
	{"spectators", spectators, METH_VARARGS, "List of client numbers of spectating clients."},

	{"playerMessage", playerMessage, METH_VARARGS, "Send a message to player."},
	{"playerMessageAll", playerMessageAll, METH_VARARGS, "Send a message as a player(from, to, text)."},
	{"playerMessageTeam", playerMessageTeam, METH_VARARGS, "Send a team message as a player(from, to, text)."},

	{"playerName", playerName, METH_VARARGS, "Get name of player from cn."},
	{"playerConnectPwd", playerConnectPwd, METH_VARARGS, "Get the connectpwd of player by cn."},
	{"playerSessionId", playerSessionId, METH_VARARGS, "Session ID of player."},
	{"playerIpLong", playerIpLong, METH_VARARGS, "Get IP of player from cn."},
	{"playerPrivilege", playerPrivilege, METH_VARARGS, "Integer representing player privilege"},
	{"playerFrags", playerFrags, METH_VARARGS, "Number of frags by player in current match."},
	{"playerTeamkills", playerTeamkills, METH_VARARGS, "Number of teamkills by player in current match."},
	{"playerDeaths", playerDeaths, METH_VARARGS, "Number of deaths by player in current match."},
	{"playerShots", playerShots, METH_VARARGS, "Shots by player in current match."},
	{"playerHits", playerHits, METH_VARARGS, "Hits by player in current match."},
	{"playerPing", playerPing, METH_VARARGS, "Current ping of player."},
	{"playerScore", playerScore, METH_VARARGS, "Flags player has scored."},
	{"playerDamageDealt", playerDamageDealt, METH_VARARGS, "Damage dealt by player in current game."},
	{"playerDamageRecieved", playerDamageRecieved, METH_VARARGS, "Damage received by player in current game."},
	{"playerTeam", playerTeam, METH_VARARGS, "Team player is member of."},
	{"playerIsSpectator", playerIsSpectator, METH_VARARGS, "Player is a spectator"},
	{"playerIsInvisible", playerIsInvisible, METH_VARARGS, "Player is invisible."},

	{"playerMapCrc", playerMapCrc, METH_VARARGS, "Map CRC of player."},
	{"playerMapName", playerMapName, METH_VARARGS, "Map name of player."},

	{"playerDisconnect", playerDisconnect, METH_VARARGS, "Disconnect player from server for a specified reason."},

	{"requestPlayerAuth", requestPlayerAuth, METH_VARARGS, "Request that a players client autoauth."},

	{"setInvisible", setInvisible, METH_VARARGS, "Set the player invisible."},
	{"setVisible", setVisible, METH_VARARGS, "Set the player visible."},
	{"spectate", spectate, METH_VARARGS, "Spectate player."},
	{"unspectate", unspectate, METH_VARARGS, "Set player to unspectated."},
	{"setStateDead", setStateDead, METH_VARARGS, "Set player state to unspectated and dead."},

	{"setPlayerTeam", setPlayerTeam, METH_VARARGS, "Set team of player."},
	{"setBotLimit", setBotLimit, METH_VARARGS, "Set server bot limit."},
	{"hashPassword", hashPass, METH_VARARGS, "Return hash for user + password"},
	{"genAuthKey", genAuthKey, METH_VARARGS, "Create auth key pair as a tuple (priv, pub)."},
	{"sendAuthChallenge", sendAuthChallenge, METH_VARARGS, "given (cn, serverDesc, id, pubkey) sends challenge to client and returns correct answer."},
	{"setMaster", setMaster, METH_VARARGS, "Set cn to master."},
	{"setAdmin", setAdmin, METH_VARARGS, "Set cn to admin."},
	{"resetPrivilege", resetPrivilege, METH_VARARGS, "Set cn to non-privileged."},

	{"setPaused", setPaused, METH_VARARGS, "Set game to be paused."},
	{"isPaused", isPaused, METH_VARARGS, "Is the game currently paused."},

	{"sendMapReload", sendMapReload, METH_VARARGS, "Causes all users to send vote on next map."},
	{"setMap", setMap, METH_VARARGS, "Set to map and mode."},
	{"setMapItems", setMapItems, METH_VARARGS, "Populate the servers entity spawn tracking data."},
	{"setMapFlags", setMapFlags, METH_VARARGS, "Populate the servers flag spawn tracking data for flag modes."},
	{"setMapBases", setMapBases, METH_VARARGS, "Populate the servers base spawn tracking data for capture modes."},

	{"masterMode", masterMode, METH_VARARGS, "Server master mode."},
	{"setMasterMode", setMasterMode, METH_VARARGS, "Set server master mode."},
	{"setMasterMask", setMasterMask, METH_VARARGS, "Set maximum master mode a master can set."},

	{"gameMode", gameMode, METH_VARARGS, "Current game mode."},
	{"mapName", mapName, METH_VARARGS, "Current map name."},
	{"modeName", modeName, METH_VARARGS, "Name of game mode."},
	{"maxClients", maxClients, METH_VARARGS, "Get current maximum number of allowed clients."},
	{"setMaxClients", setMaxClients, METH_VARARGS, "Set maximum number of allowed clients."},

	{"uptime", uptime, METH_VARARGS, "Number of milliseconds server has been running."},

	{"authChallenge", authChal, METH_VARARGS, "Send auth challenge to client."},

	{"secondsRemaining", secondsLeft, METH_VARARGS, "seconds remaining in current match."},
	{"setSecondsRemaining", setSecondsLeft, METH_VARARGS, "Set the number of seconds remaining in current game."},

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

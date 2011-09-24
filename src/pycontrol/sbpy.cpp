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

#include "sbpy.h"
#include "server.h"

#include <string>
#include <iostream>

extern int totalmillis;

namespace SbPy
{

static char *plugin_path;
static char *pn;

void loadPluginPath()
{
	char *path = getenv("CXSBS_PLUGIN_PATH");
	if(!path)
		plugin_path = path;
}

void loadPythonRoot()
{
	char *path = getenv("CXSBS_PYTHON_ROOT");
	if(!path)
		plugin_path = path;
}

PyMODINIT_FUNC initModule(void);

#define SBPY_ERR(x) \
	if(!x) \
	{ \
		if(PyErr_Occurred()) \
			PyErr_Print(); \
		return false;\
	}

PyObject *callPyStringFunc(PyObject *func, const char *text)
{
	PyObject *val, *pArgs, *pText;

	//check the function
	if(!func || !PyCallable_Check(func))
	{
		fprintf(stderr, "Python Error: Invalid handler to triggerEvent function.\n");
		return val;
	}

	//construct the args
	pArgs = PyTuple_New(1);
	pText = PyString_FromString(text);
	SBPY_ERR(pText)
	PyTuple_SetItem(pArgs, 0, pText);

	val = PyObject_CallObject(func, pArgs);
	Py_DECREF(pArgs);
	if(!val)
		PyErr_Print();
	return val;
}

static PyObject *cxsbsModule, *loadPluginsFunction, *getResourceFunction;
static PyObject *eventsModule, *triggerEventFunc, *triggerPolicyEventFunc, *updateFunc;
static PyObject *textModerationModule, *textModFunc;

bool initPy()
{
	PyRun_SimpleString("import sys\nimport os\nsys.path.append(os.getcwd())");

	cxsbsModule = PyImport_ImportModule("cxsbs");
	SBPY_ERR(cxsbsModule)

	loadPluginsFunction = PyObject_GetAttrString(cxsbsModule, "loadPlugins");
	SBPY_ERR(loadPluginsFunction);
	if(!PyCallable_Check(loadPluginsFunction))
	{
		fprintf(stderr, "Error: loadPlugins function could not be loaded.\n");
		return false;
	}

	//Actually load the plugins...
	callPyStringFunc(loadPluginsFunction, plugin_path);

	//get the rest of the c++ accessible resources
	getResourceFunction = PyObject_GetAttrString(cxsbsModule, "getResource");
	SBPY_ERR(getResourceFunction);
	if(!PyCallable_Check(getResourceFunction))
	{
		fprintf(stderr, "Error: getResource function could not be loaded.\n");
		return false;
	}
	
	//Get the Events plugin
	eventsModule = callPyStringFunc(getResourceFunction, "Events");
	SBPY_ERR(eventsModule)

	//get the stuff we need out of the Events plugin
	triggerEventFunc = PyObject_GetAttrString(eventsModule, "triggerServerEvent");
	SBPY_ERR(triggerEventFunc);
	if(!PyCallable_Check(triggerEventFunc))
	{
		fprintf(stderr, "Error: triggerEvent function could not be loaded.\n");
		return false;
	}

	triggerPolicyEventFunc = PyObject_GetAttrString(eventsModule, "triggerPolicyEvent");
	SBPY_ERR(triggerPolicyEventFunc);
	if(!PyCallable_Check(triggerPolicyEventFunc))
	{
		fprintf(stderr, "Error: triggerPolicyEvent function could not be loaded.\n");
		return false;
	}

	updateFunc = PyObject_GetAttrString(eventsModule, "update");
	SBPY_ERR(updateFunc);
	if(!PyCallable_Check(updateFunc))
	{
		fprintf(stderr, "Error: update function could not be loaded.\n");
		return false;
	}

	//Get the textModeration plugin
	textModerationModule = callPyStringFunc(getResourceFunction, "TextModeration");
	SBPY_ERR(textModerationModule)

	textModFunc = PyObject_GetAttrString(textModerationModule, "textModerate");
	SBPY_ERR(textModFunc);
	if(!PyCallable_Check(textModFunc))
	{
		fprintf(stderr, "Error: textModerate function could not be loaded.\n");
		return false;
	}

	return true;
}

void deinitPy()
{
	Py_XDECREF(cxsbsModule);
	Py_XDECREF(loadPluginsFunction);
	Py_XDECREF(getResourceFunction);

	Py_XDECREF(eventsModule);
	Py_XDECREF(triggerEventFunc);
	Py_XDECREF(triggerPolicyEventFunc);
	Py_XDECREF(updateFunc);

	Py_XDECREF(textModerationModule);
	Py_XDECREF(textModFunc);

	Py_Finalize();
}

bool init(const char *programName, const char *pythonRoot, const char *pluginPath, const char *instanceRoot)
{
	// Setup env vars and chdir
	if(!pn)
	{
		pn = new char[strlen(programName)+1];
		strcpy(pn, programName);
	}

	if(pluginPath[0] || plugin_path)
	{
		if(!plugin_path)
		{
			plugin_path = new char[strlen(pluginPath)+1];
			strcpy(plugin_path, pluginPath);
		}
	}
	else loadPluginPath();

	if(!plugin_path)
	{
		fprintf(stderr, "Fatal Error: Could not locate a plugin directory.\n");
		return false;
	}

	// Set program name
	Py_SetProgramName(pn);

	// Initialize
	Py_Initialize();
	initModule();
	if(!initPy())
	{
		fprintf(stderr, "Error retrieving core python resources modules.\n");
		return false;
	}
	return true;
}

PyObject *callPyFunc(PyObject *func, PyObject *args)
{
	PyObject *val;
	val = PyObject_CallObject(func, args);
	Py_DECREF(args);
	if(!val)
		PyErr_Print();
	return val;
}

const char *textModerate(const char *type, int cn, const char *text, PyObject *func)
{
	PyObject *pArgs, *pType, *pCn, *pText, *pValue;
	std::vector<PyObject*>::const_iterator itr;
	int i = 0;
	
	if(!func)
	{
		//fprintf(stderr, "Python Error: Invalid handler to triggerEvent function.\n");
		std::cerr << "Python Error: Invalid handler to triggerEvent function when triggering text moderator type:" << type << std::endl;
		return false;
	}
	pArgs = PyTuple_New(3);
	
	pType = PyString_FromString(type);
	pCn = PyInt_FromLong(cn);
	pText = PyString_FromString(text);
	
	SBPY_ERR(pType)
	SBPY_ERR(pText)
	
	PyTuple_SetItem(pArgs, 0, pType);
	PyTuple_SetItem(pArgs, 1, pCn);
	PyTuple_SetItem(pArgs, 2, pText);

	pValue = callPyFunc(func, pArgs);

	if(!pValue)
	{
		fprintf(stderr, "Error moderating text.\n");
		return false;
	}

    	return PyString_AsString(pValue);
}

bool triggerFuncEvent(const char *name, std::vector<PyObject*> *args, PyObject *func)
{
	PyObject *pArgs, *pArgsArgs, *pName, *pValue;
	std::vector<PyObject*>::const_iterator itr;
	int i = 0;
	
	if(!func)
	{
		std::cerr << "Python Error: Invalid handler to triggerEvent function when triggering event:" << name << std::endl;
		return false;
	}
	pArgs = PyTuple_New(2);
	pName = PyString_FromString(name);
	SBPY_ERR(pName)
	PyTuple_SetItem(pArgs, 0, pName);
	if(args)
	{
		pArgsArgs = PyTuple_New(args->size());
		for(itr = args->begin(); itr != args->end(); itr++)
		{
			PyTuple_SetItem(pArgsArgs, i, *itr);
			i++;
		}
	}
	else
		pArgsArgs = PyTuple_New(0);
	PyTuple_SetItem(pArgs, 1, pArgsArgs);
	pValue = callPyFunc(func, pArgs);
	if(!pValue)
	{
		fprintf(stderr, "Error triggering event.\n");
		return false;
	}
	if(PyBool_Check(pValue))
	{
		bool ret = (pValue == Py_True);
		Py_DECREF(pValue);
		return ret;
	}
	Py_DECREF(pValue);
	return true;
}

#undef SBPY_ERR

bool triggerFuncEventInt(const char *name, int cn, PyObject *func)
{
	std::vector<PyObject*> args;
	PyObject *pCn = PyInt_FromLong(cn);
	args.push_back(pCn);
	return triggerFuncEvent(name, &args, func);
}

bool triggerFuncEventString(const char *name, const char *str, PyObject *func)
{
	std::vector<PyObject*> args;
	PyObject *pCn = PyString_FromString(str);
	args.push_back(pCn);
	return triggerFuncEvent(name, &args, func);
}

bool triggerFuncEventIntBool(const char *name, int cn, bool b, PyObject *func)
{
	std::vector<PyObject*> args;
	PyObject *pCn = PyInt_FromLong(cn);
	PyObject *pB;
	if(b)
		pB = Py_True;
	else
		pB = Py_False;
	args.push_back(pCn);
	args.push_back(pB);
	
	return triggerFuncEvent(name, &args, func);
}

bool triggerFuncEventIntString(const char *name, int cn, const char *text, PyObject *func)
{
	std::vector<PyObject*> args;
	PyObject *pText = PyString_FromString(text);
	PyObject *pCn = PyInt_FromLong(cn);
	args.push_back(pCn);
	args.push_back(pText);
	return triggerFuncEvent(name, &args, func);
}

bool triggerFuncEventIntStringInt(const char *name, int cn, const char *text, int cn2, PyObject *func)
{
	std::vector<PyObject*> args;
	PyObject *pText = PyString_FromString(text);
	PyObject *pCn = PyInt_FromLong(cn);
	PyObject *pCn2 = PyInt_FromLong(cn2);
	args.push_back(pCn);
	args.push_back(pText);
	args.push_back(pCn2);
	return triggerFuncEvent(name, &args, func);
}

bool triggerFuncEventIntInt(const char *name, int cn, int cn2, PyObject *func)
{
	std::vector<PyObject*> args;
	PyObject *pCn = PyInt_FromLong(cn);
	PyObject *pCn2 = PyInt_FromLong(cn2);
	args.push_back(pCn);
	args.push_back(pCn2);
	return triggerFuncEvent(name, &args, func);
}

bool triggerFuncEventIntStringString(const char *name, int cn, const char *text, const char *text2, PyObject *func)
{
	std::vector<PyObject*> args;
	PyObject *pText2 = PyString_FromString(text2);
	PyObject *pText = PyString_FromString(text);
	PyObject *pCn = PyInt_FromLong(cn);
	args.push_back(pCn);
	args.push_back(pText);
	args.push_back(pText2);
	return triggerFuncEvent(name, &args, func);
}

const char *moderateText(const char *type, int cn, const char *text)
{
	return textModerate(type, cn, text, textModFunc);
}

bool triggerEvent(const char*name, std::vector<PyObject*>* args)
{
	return triggerFuncEvent(name, args, triggerEventFunc);
}

bool triggerEventInt(const char *name, int cn)
{
	return triggerFuncEventInt(name, cn, triggerEventFunc);
}

bool triggerEventIntBool(const char *name, int cn, bool b)
{
	return triggerFuncEventIntBool(name, cn, b, triggerEventFunc);
}

bool triggerEventStr(const char *name, const char *str)
{
	return triggerFuncEventString(name, str, triggerEventFunc);
}

bool triggerEventIntString(const char *name, int cn, const char *text)
{
	return triggerFuncEventIntString(name, cn, text, triggerEventFunc);
}

bool triggerEventIntStringInt(const char *name, int n, const char *str, int n2)
{
	return triggerFuncEventIntStringInt(name, n, str, n2, triggerEventFunc);
}

bool triggerEventIntStringString(const char *name, int cn, const char *text, const char *text2)
{
	return triggerFuncEventIntStringString(name, cn, text, text2, triggerEventFunc);
}

bool triggerEventIntInt(const char *name, int cn1, int cn2)
{
	std::vector<PyObject*> args;
	PyObject *pCn1 = PyInt_FromLong(cn1);
	PyObject *pCn2 = PyInt_FromLong(cn2);
	args.push_back(pCn1);
	args.push_back(pCn2);
	return triggerFuncEvent(name, &args, triggerEventFunc);
}

bool triggerEventIntIntString(const char *name, int cn1, int cn2, const char *text)
{
	std::vector<PyObject*> args;
	PyObject *pCn1 = PyInt_FromLong(cn1);
	PyObject *pCn2 = PyInt_FromLong(cn2);
	PyObject *pTxt = PyString_FromString(text);
	args.push_back(pCn1);
	args.push_back(pCn2);
	args.push_back(pTxt);
	return triggerFuncEvent(name, &args, triggerEventFunc);
}

bool triggerEventStrInt(const char *name, const char *str, int n)
{
	std::vector<PyObject*> args;
	PyObject *pstr, *pn;
	pstr = PyString_FromString(str);
	pn = PyInt_FromLong(n);
	args.push_back(pstr);
	args.push_back(pn);
	return triggerFuncEvent(name, &args, triggerEventFunc);
}

bool triggerPolicyEventInt(const char *name, int cn)
{
	return triggerFuncEventInt(name, cn, triggerPolicyEventFunc);
}

bool triggerPolicyEventIntInt(const char *name, int cn, int tcn)
{
	return triggerFuncEventIntInt(name, cn, tcn, triggerPolicyEventFunc);
}

bool triggerPolicyEventIntString(const char *name, int cn, const char *text)
{
	return triggerFuncEventIntString(name, cn, text, triggerPolicyEventFunc);
}

void update()
{
	PyObject *pargs, *pvalue;
	pargs = PyTuple_New(0);
	pvalue = callPyFunc(updateFunc, pargs);
	if(pvalue)
		Py_DECREF(pvalue);
}

}

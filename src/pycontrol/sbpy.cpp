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

#include <stdio.h>
#include <stdarg.h>
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

//Objects associated with pyTensible
static PyObject *pyTensibleModule, *PluginLoaderClass, *plugin_loaderObject, *setup_loggingFunction, *load_pluginsFunction, *get_resourceFunction;

//Objects associated with org.cxsbs.system
static PyObject *trigger_eventFunction, *updateFunction;

bool initPy()
{
	PyRun_SimpleString("import sys, os");
	//PyRun_SimpleString("sys.path.append(os.getcwd())");
	PyRun_SimpleString("sys.path.append(os.path.abspath('pydeps'))");

	//import pyTensible
	pyTensibleModule = PyImport_ImportModule("pyTensible");
	SBPY_ERR(pyTensibleModule)

	//get the setup_logging function
	setup_loggingFunction = PyObject_GetAttrString(pyTensibleModule, "setup_logging");
	SBPY_ERR(setup_loggingFunction)
	if(!PyCallable_Check(setup_loggingFunction))
	{
		fprintf(stderr, "Error: setup_logging function could not be loaded from pyTensible.\n");
		return false;
	}

	//set the logging path for pyTensible
	callPyStringFunc(setup_loggingFunction, "plugin_loader.log");

	//plugin_loader = pyTensible.PluginLoader()
	PluginLoaderClass = PyObject_GetAttrString(pyTensibleModule, "PluginLoader");
	SBPY_ERR(PluginLoaderClass)
	if(!PyCallable_Check(PluginLoaderClass))
	{
		fprintf(stderr, "Error: PluginLoader class could not be loaded from pyTensible.\n");
		return false;
	}

	//"instantiate" the plugin_loader (really bootstraps one out of the base pyTensible plug-ins)
	plugin_loaderObject = PyObject_CallObject(PluginLoaderClass, PyTuple_New(0));
	SBPY_ERR(plugin_loaderObject);

	//get the function to load plug-ins from the plugin_loader object
	load_pluginsFunction = PyObject_GetAttrString(plugin_loaderObject, "load_plugins");
	SBPY_ERR(load_pluginsFunction);
	if(!PyCallable_Check(load_pluginsFunction))
	{
		fprintf(stderr, "Error: load_plugins function could not be loaded from the plugin_loader object.\n");
		return false;
	}

	//Actually load the plugins...
	callPyStringFunc(load_pluginsFunction, plugin_path);

	//get the get_resource function
	get_resourceFunction = PyObject_GetAttrString(plugin_loaderObject, "get_resource");
	SBPY_ERR(get_resourceFunction);
	if(!PyCallable_Check(get_resourceFunction))
	{
		fprintf(stderr, "Error: get_resource function could not be loaded.\n");
		return false;
	}

	//get the rest of the c++ accessible resources

	
	//Get trigger_event function
	trigger_eventFunction = callPyStringFunc(get_resourceFunction, "org.cxsbs.core.events.trigger_event");
	SBPY_ERR(trigger_eventFunction)
	if(!PyCallable_Check(trigger_eventFunction))
	{
		fprintf(stderr, "Error: trigger_event function could not be loaded from 'org.cxsbs.core.events.trigger_event'.\n");
		return false;
	}

	//get the update function to call on each server slice
	updateFunction = callPyStringFunc(get_resourceFunction, "org.cxsbs.core.slice.update");
	SBPY_ERR(updateFunction);
	if(!PyCallable_Check(updateFunction))
	{
		fprintf(stderr, "Error: update function could not be loaded from 'org.cxsbs.core.slice.update'.\n");
		return false;
	}

	return true;
}

void deinitPy()
{

	Py_XDECREF(pyTensibleModule);

	Py_XDECREF(PluginLoaderClass);
	Py_XDECREF(plugin_loaderObject);
	Py_XDECREF(setup_loggingFunction);

	Py_XDECREF(load_pluginsFunction);
	Py_XDECREF(get_resourceFunction);

	Py_XDECREF(trigger_eventFunction);
	Py_XDECREF(updateFunction);

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

bool triggerEvent(const char*name, std::vector<PyObject*>* args)
{
	return triggerFuncEvent(name, args, trigger_eventFunction);
}

bool triggerEventf(const char *event_name, const char* format, ... )
{
      va_list arguments;
      va_start(arguments, format);

      std::vector<PyObject*> args;

      for(int i = 0; format[i] != '\0'; ++i )
      {
            if (format[i] == 'b')
            {
            	args.push_back(PyBool_FromLong(va_arg(arguments, int)));
            }
            else if (format[i] == 'f')
            {
            	args.push_back(PyFloat_FromDouble(va_arg(arguments, double)));
            }
            else if (format[i] == 'i')
            {
            	args.push_back(PyInt_FromLong(va_arg(arguments, int)));
            }
            else if (format[i] == 'l')
            {
            	args.push_back(PyLong_FromLong(va_arg(arguments, long)));
            }
            else if (format[i] == 'p')
            {
            	args.push_back(va_arg(arguments, PyObject *));
            }
            else if (format[i] == 'c')
            {
            	args.push_back(PyString_FromFormat("%c", va_arg(arguments, int)));
            }
            else if (format[i] == 's')
            {
            	args.push_back(PyString_FromString(va_arg(arguments, char *)));
            }
      }
      va_end(arguments);

      return triggerFuncEvent(event_name, &args, trigger_eventFunction);

}

bool reload_on_update = false;

bool update()
{
	if (reload_on_update)
	{
		// Deinitialize
		deinitPy();
		// Initialize
		Py_Initialize();
		initModule();
		if(!initPy())
		{
			fprintf(stderr, "Error retrieving core Python resources modules on reload.\n");
			return false;
		}
		reload_on_update = false;
	}

	PyObject *pargs, *pvalue;
	pargs = PyTuple_New(0);
	pvalue = callPyFunc(updateFunction, pargs);
	if(pvalue)
		Py_DECREF(pvalue);
	return true;
}

}

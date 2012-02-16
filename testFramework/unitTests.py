#####################################################################
""""Unit Test framework that works in both eclipse and Commandline"""
#####################################################################

if __name__ == "__main__":
	import os
	import sys
	import re
	import inspect
	xsbsPath = os.path.abspath("../")
	sys.path.append(xsbsPath)
	sys.path.append(xsbsPath + "/pyscripts/")
	del xsbsPath

#####################################################################
""""Import the test cases"""
#####################################################################

#xsbs.net
from xsbs.net import NetTestCase

#xsbs.groups
from xsbs.groups import GroupTestCase

#####################################################################
""""Don't modify below here"""
#####################################################################

if __name__ == "__main__":
	testClasses = []
	gvarkeys = globals().keys()
	
	import unittest
	
	for key in gvarkeys:
		gvar = globals()[key]
		#if re.search("TestCase$", key):
		if inspect.isclass(gvar) and issubclass(gvar, unittest.TestCase):
			testClasses.append(gvar)
		
	import coverage
		
	cov = coverage.coverage()
	cov.start()
	
	suite = unittest.TestSuite()
	
	for classHandler  in testClasses:
		for name, value in inspect.getmembers(classHandler, callable):
			if re.match("test", name):
				suite.addTest(classHandler(name))
	
	runner = unittest.TextTestRunner(verbosity=2)
	runner.run(suite)
	
	cov.stop()
	cov.html_report(directory='unitTestCoverage')
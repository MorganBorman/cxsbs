from Group import Group
from DynamicGroup import DynamicGroup
from Query import Query

from Query import Contains, Not, Select, Intersection
	
import unittest

class GroupTestCase(unittest.TestCase):
	import Errors
	import Query.Errors
	
	class ExampleClass:
		def __init__(self, name):
			self.Name = name
		
		def name(self):
			return self.Name
	
	base = [ExampleClass("[FD]Chasm"), ExampleClass("[FD]Oblivion"), ExampleClass("|DM|Broski"), ExampleClass("|DM|Dannyboy")]
	
	class DynamicBase:
		def __init__(self, base):
			"""Will expose one more of the given base on each access"""
			self.position = 0
			self.base = base
		
		def __call__(self):
			self.position += 1
			return self.base[:self.position]
	
	def testEmptyGroupCreation(self):
		emptyGroup = Group(self.ExampleClass)
		self.assertEquals(emptyGroup.members(), [])
	
	def testGroupCreation(self):
		exampleGroup = Group(self.ExampleClass, self.base) #@UnusedVariable
	
	def testInvalidMember(self):
		exampleGroup = Group(self.ExampleClass, self.base)
		self.assertRaises(self.Errors.NonCongruentGroup, exampleGroup.append, 5)
	
	def testStaticGroups(self):
		exampleGroup = Group(self.ExampleClass, self.base)
		self.assertEquals(str(exampleGroup.action("name", ())), str(['[FD]Chasm', '[FD]Oblivion', '|DM|Broski', '|DM|Dannyboy']))
	
	def testDynamicGroups(self):
		exampleDynamicBase = self.DynamicBase(self.base)
		exampleDynamicGroup = DynamicGroup(self.ExampleClass, exampleDynamicBase)
		self.assertEquals(len(exampleDynamicGroup.members()), 1)
		self.assertEquals(len(exampleDynamicGroup.members()), 2)
		self.assertEquals(len(exampleDynamicGroup.members()), 3)
		self.assertEquals(str(exampleDynamicGroup.action("name", ())), str(['[FD]Chasm', '[FD]Oblivion', '|DM|Broski', '|DM|Dannyboy']))
		
	def testGroupIteration(self):
		exampleGroup = Group(self.ExampleClass, self.base)
		count = 0
		for item in exampleGroup: #@UnusedVariable
			count += 1
		self.assertEquals(count, 4)
			
	def testDynamicGroupIteration(self):
		exampleDynamicBase = self.DynamicBase(self.base)
		exampleDynamicGroup = DynamicGroup(self.ExampleClass, exampleDynamicBase)
		count = 0
		for i in range(4): #@UnusedVariable
			for item in exampleDynamicGroup: #@UnusedVariable
				count += 1
		self.assertEquals(count, 10)
		
	def testQueries(self):
		exampleGroup = Group(self.ExampleClass, self.base)
		exampleFilter = Select(name=Contains("[FD]"))
		exampleQuery = exampleGroup.query(exampleFilter)
		self.assertEquals(str(exampleQuery.all().action("name", ())), str(['[FD]Chasm', '[FD]Oblivion']))
		
	def testInvalidAction(self):
		exampleGroup = Group(self.ExampleClass, self.base)
		self.assertRaises(self.Errors.InvalidGroupAction, exampleGroup.action, "not_member_method", ())
	
	def testInvalidFilterParameter(self):
		exampleGroup = Group(self.ExampleClass, self.base)
		exampleFilter = Select(nsdfame=Contains("[FD]"))
		exampleQuery = exampleGroup.query(exampleFilter)
		self.assertRaises(self.Errors.InvalidProperty, exampleQuery.all)
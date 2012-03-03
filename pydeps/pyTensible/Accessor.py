'''
Requirements
-------------
Not static. If the source dictionary hierarchy changes then access should still be available to updated items.

Items in the dictionary hierarchy are accessed using the infix notation.

test = Accessor({'foo': {'bar': {'baz': "bozo"}}}, {})

assert(test.foo.bar.baz == "bozo")

test2 = test.foo

assert(test2.bar.baz == "bozo")

test.bar should raise AttributeError()
'''
from Namespace import Namespace

class Accessor:
	def __init__(self, namespace, namespace_hierarchy):
		'''
		Accessors are the key to pyTensible. Basically an Accessor is an alias to the loaded interfaces/resources within pyTensible
		
		If strict=False then the Accessor is lazily evaluated. This means it does not throw an exception at runtime if the specified
		namespace does not exist.
		'''
		self.__namespace = namespace
		self.__namespace_hierarchy = namespace_hierarchy
	
	def __getattr__(self, name):
		try:
			target_self = get_nested_dictionary(self.__namespace, self.__namespace_hierarchy)
			if isinstance(target_self, Namespace):
				return target_self.__getattr__(name)
		except KeyError:
			raise AttributeError(name)
		
		try:
			target = get_nested_dictionary(self.__namespace + [name], self.__namespace_hierarchy)
		except KeyError:
			raise AttributeError(name)
			
		if isinstance(target, Namespace):
			return target
		else:
			sub_accessor = Accessor(self.__namespace + [name], self.__namespace_hierarchy)
			return sub_accessor
	
	def __setattr__(self, name, value):
		if name in ["_Accessor__namespace", "_Accessor__namespace_hierarchy"]:
			self.__dict__[name] = value
		else:
			raise AttributeError(name)
	
	def __delattr__(self, name):
		raise AttributeError(name)
	
def get_nested_dictionary(namespace, dictionary):
	position = namespace[:]
	nested = dictionary
	
	while len(position) > 0:
		key = position.pop(0)
		
		nested = nested[key]
		
	return nested
	
import unittest

class TestAccessors(unittest.TestCase):

	def setUp(self):
		self.broken_namespace = Namespace({'IName': "IName Interface"}, {'Name': "Name class"})
		self.alphabet_namespace = Namespace({'ILetter': "ILetter Interface"}, {'Letter': "Letter class"})
		
		self.test_accessor = Accessor([], {'foo': {'bar': {'baz': self.broken_namespace}}})

	def test_first(self):
		a_namespace = self.test_accessor.foo.bar.baz
		self.assertTrue(isinstance(a_namespace, Namespace))
		self.assertEqual(a_namespace, self.broken_namespace)
		
	def test_second(self):
		an_accessor = self.test_accessor.foo
		self.assertEqual(an_accessor.bar.baz, self.test_accessor.foo.bar.baz)
		
	def test_third(self):
		self.assertEqual(self.test_accessor.foo.bar.baz.IName, "IName Interface")
		self.assertEqual(self.test_accessor.foo.bar.baz.Name, "Name class")
		
	def get_fish(self, an_object):
		return an_object.fish
		
	def test_bad(self):
		self.assertRaises(AttributeError, self.get_fish, self.test_accessor)

if __name__ == '__main__':
	unittest.main()
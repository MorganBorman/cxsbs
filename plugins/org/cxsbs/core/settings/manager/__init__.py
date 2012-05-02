import pyTensible, org, CategoryConfig

class manager(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		self.settings_manager = SettingsManager()
		
		SettingDecorator = create_decorator(self.settings_manager)
		SettingAccessor = create_accessor_class(self.settings_manager)
		
		event_manager = org.cxsbs.core.events.manager.event_manager
		event_manager.register_handler('server_start', self.settings_manager.on_started)
		
		Interfaces = {}
		Resources = {'settings_manager': self.settings_manager, 'Setting': SettingDecorator(), 'Accessor': SettingAccessor}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
def bstrip(string):
	characters = "\t "
	return string.lstrip(characters).rstrip(characters)

def read_setting_docstring(docstring):
	doc_lines = docstring.split('\n')
	
	doc = []
	
	category = ""
	display_name = ""
	wbpolicy = ""
	docstring = ""
	
	is_doc = False
	for doc_line in doc_lines:
		doc_line = bstrip(doc_line)
		doc_line_tokens = doc_line.split(None, 2)
		if len(doc_line_tokens) <= 0:
			pass
		elif doc_line_tokens[0] == "@category":
			is_doc = False
			category = doc_line_tokens[1]
		elif doc_line_tokens[0] == "@display_name":
			is_doc = False
			display_name = ' '.join(doc_line_tokens[1:])
		elif doc_line_tokens[0] == "@wbpolicy":
			is_doc = False
			wbpolicy = doc_line_tokens[1]
		elif doc_line_tokens[0] == "@doc":
			if len(doc_line) >= 6:
				doc_line = doc_line[5:]
			else:
				doc_line = ""
			is_doc = True
			
		if is_doc:
			doc.append(doc_line)
			
	while doc[-1] == "":
		doc = doc[:-1]
		
	docstring = "\n".join(doc)
	
	return category, display_name, wbpolicy, docstring
	
def create_decorator(settings_manager):
	class SettingDecorator(object):
		'''Decorator which registers a setting with the settings manager.'''
		def __init__(self):
			self.setting_classes = pyTensible.plugin_loader.get_providers("org.cxsbs.core.settings.interfaces.ISetting")
			
		def __call__(self, f):
			setting_symbolic_name = f.__module__ + '.' + f.__name__
			setting_category, setting_display_name, setting_default_wbpolicy, setting_doc = read_setting_docstring(f.__doc__)
			setting_default_value = f()
			
			for setting_class in self.setting_classes.values():
				if setting_class.handles_type(type(setting_default_value)):
					setting_object = setting_class(setting_category, setting_symbolic_name, setting_display_name, setting_default_value, setting_default_wbpolicy, setting_doc)
				
					settings_manager.add(setting_object)
					
					return setting_object
				
			raise org.cxsbs.core.settings.exceptions.InvalidSettingType("There does not seem to be a Setting to handle this type (%s)." %type(setting_default_value) )
		
	return SettingDecorator

def create_accessor_class(settings_manager):
	class SettingAccessor(object):
		def __init__(self, namespace=None):
			"""
			namespace is the local namespace of this Accessor meaning settings 
			within this namespace can be accessed without their fully qualified names.
			
			If no namespace is provided then all names must be fully qualified.
			
			A setting is assumed to be a local reference if it contains no '.' and global otherwise.
			"""
			self._namespace = namespace
			
		def __getitem__(self, key):
			if not '.' in key:
				key = self._namespace + '.' + key
				
			return settings_manager.get_setting(key).value
		
		def __setitem__(self, key, value):
			if not '.' in key:
				key = self._namespace + '.' + key
				
			settings_manager.get_setting(key).value = value
			
	return SettingAccessor
	
class SettingsManager(org.cxsbs.core.settings.interfaces.ISettingsManager):
	"""
	The interface with which settings are managed and accessed.
	"""
	#a dictionary of the settings objects keyed by the full symbolic name
	_by_symbolic_name = {}
	_by_namespace = {}
	_setting_store = None
	
	def __init__(self):
		self._by_symbolic_name = {}
		self._by_namespace = {}
		
		#TODO make this have a settings file in the instance root and use that to determine which
		#SettingStore to use and where to store the rest of the settings.
		
		store_classes = pyTensible.plugin_loader.get_providers("org.cxsbs.core.settings.interfaces.ISettingStore")
		
		config_path = org.cxsbs.core.server.instance.root
		config_category = "settings"
		config_extension = ".conf"
		
		config_object = CategoryConfig.CategoryConfig(config_path, config_category, config_extension)
		doc = 'Which settings store should be used. Look at the section name below for the fully qualified SettingStore names.'
		store = config_object.getOption('org.cxsbs.core.settings.manager.store', 'org.cxsbs.core.settings.nullstore.NullStore', doc)
		
		for store_class in store_classes.values():
			store_class.initialize_config( config_object )
			
		store_class = store_classes[store]
		
		self._setting_store = store_class(config_object)
	
	def get_setting(self, symbolic_name):
		"""
		Get a setting object by symbolic_name.
		"""
		if symbolic_name in self._by_symbolic_name.keys():
			return self._by_symbolic_name[symbolic_name]
		else:
			raise org.cxsbs.core.settings.exceptions.InvalidSettingReference(symbolic_name)
		
	def on_started(self, event):
		"Called when the server starts. After all the plug-ins have loaded."
		self._setting_store.finalize_initialization()
	
	def add(self, setting_object):
		"Add a setting object as managed and initializes it with the configured SettingStore."
		namespace, handle = setting_object.symbolic_name.rsplit('.', 1)

		if namespace not in self._by_namespace.keys():
			self._by_namespace[namespace] = {}
			
		self._by_namespace[namespace][handle] = setting_object
		
		self._by_symbolic_name[setting_object.symbolic_name] = setting_object
		
		self._setting_store.initialize(setting_object)
	
	def reload(self):
		"Reload all added settings from the indicated SettingStore."
		for setting_object in self._by_symbolic_name.values():
			self._setting_store.read(setting_object)
	
	def reset(self):
		"Revert all settings to their defaults. This may cause those settins with 'immediate' writeback policies to be stored."
		for setting_object in self._by_symbolic_name.values():
			setting_object.value = setting_object.default
	
	def writeback(self):
		"Request that this setting store all dirty settings whose policies do not forbid write-back."
		for setting_object in self._by_symbolic_name.values():
			self._setting_store.write(setting_object)
	
	def notify(self, setting_object):
		"""
		Used by a setting object whose 'possess' feild has been populated, to notify the SettingsManager that a change has occurred.
		And to take action as necessary with respect to the writeback policy of the setting.
		
		Setting objects should do this even if their values never get written back.
		"""
		if setting_object.wbpolicy == "never":
			pass
		elif setting_object.wbpolicy == "immediate":
			self._setting_store.write(setting_object)
		elif setting_object.wbpolicy == "explicit":
			pass
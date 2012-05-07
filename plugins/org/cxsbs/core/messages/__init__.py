import pyTensible, org

import string

from groups.DynamicGroup import DynamicGroup
from groups.Group import Group

import operator
from groups.Query import Select, Compare

class messages(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        Interfaces = {}
        Resources = {'Message': MessageDecorator}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
def bstrip(string):
    characters = "\t "
    return string.lstrip(characters).rstrip(characters)

def read_message_docstring(docstring):
    doc_lines = docstring.split('\n')
    
    doc = []
    
    fields = []
    docstring = ""
    
    is_doc = False
    for doc_line in doc_lines:
        doc_line = bstrip(doc_line)
        doc_line_tokens = doc_line.split(None, 2)
        if len(doc_line_tokens) <= 0:
            pass
        elif doc_line_tokens[0] == "@fields":
            is_doc = False
            if len(doc_line_tokens) > 1:
                fields += doc_line_tokens[1].split()
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
    
    return fields, docstring

def form_message(template, fields, submessages):
    if fields is None:
        fields = {}
        
    if submessages is None:
        submessages = {}
        
    for field_name, (submessage_template, submessage_fields) in submessages.items():
        fields[field_name] = form_message(submessage_template, submessage_fields, {})
        
    fields.update(org.cxsbs.core.ui.colors.colordict)
    fields.update(org.cxsbs.core.ui.prefixes.get_prefix_dict())
    
    return template.safe_substitute(fields)

class Message(org.cxsbs.core.settings.types.Template.Setting):
    def __init__(self, symbolic_name, fields, default_template_string, doc_string):
        org.cxsbs.core.settings.types.Template.Setting.__init__(
                                                                    self,
                                                                    category = "messages", 
                                                                    symbolic_name = symbolic_name, 
                                                                    default_value = string.Template(default_template_string), 
                                                                    default_wbpolicy = "never", 
                                                                    doc = doc_string + "\n" + "available message specific fields: %s" % ", ".join(fields)
                                                               )
        
        org.cxsbs.core.settings.manager.settings_manager.add(self)
    
    def server(self, target=None, fields=None, submessages=None):
        """
        Sends this message as a server message to target
        
        target: a None, Client, or Group to message
        fields: a dictionary of values to substitute into the template fields
            fields[field_name] = "field value"
        submessages: a dictionary of (template, fields) pairs keyed by field name which need to be evaluated before substitution.
            submessages[field_name] = (submessage_template, {submessage_field_name: "field value"})
        """
        message_template = self.value
        
        if target is None:
            target = org.cxsbs.core.clients.AllClientsGroup
        elif isinstance(target, org.cxsbs.core.clients.Client):
            target = Group(org.cxsbs.core.clients.Client, [target])
            
        if not isinstance(target, Group):
            raise Exception()
            
        target = target.query(Select(cn=Compare(127, operator=operator.le))).all()
        
        if len(target.members()) < 1:
            return
        
        message_data = form_message(message_template, fields, submessages)
        
        target.action("message", (message_data,))
    
    def say(self, speaker=None, target=None, fields=None, submessages=None):
        """
        Send a chat message as speaker to target
        
        speaker: a client to send the message as
        target: a None, Client, or Group to message
        fields: a dictionary of values to substitute into the template fields
            fields[field_name] = "field value"
        submessages: a dictionary of (template, fields) pairs keyed by field name which need to be evaluated before substitution.
            submessages[field_name] = (submessage_template, {submessage_field_name: "field value"})
        """
        message_template = self.value
        
        if target is None:
            target = org.cxsbs.core.clients.AllClientsGroup
        elif isinstance(target, org.cxsbs.core.clients.Client):
            target = Group(org.cxsbs.core.clients.Client, [target])
            
        if not isinstance(target, Group):
            raise Exception()
        
        if not isinstance(speaker, org.cxsbs.core.clients.Client):
            raise Exception()
            
        target = target.query(Select(cn=Compare(127, operator=operator.le))).all()
        
        if len(target.members()) < 1:
            return
        
        message_data = form_message(message_template, fields, submessages)
        
        for client in group.members():
            speaker.say(client.cn, message_data)
    
    def sayteam(self, speaker=None, target=None, fields=None, submessages=None):
        """
        Send a team chat message as speaker to target
        
        speaker: client to send the message as
        target: a None, Client, or Group to message
        fields: a dictionary of values to substitute into the template fields
            fields[field_name] = "field value"
        submessages: a dictionary of (template, fields) pairs keyed by field name which need to be evaluated before substitution.
            submessages[field_name] = (submessage_template, {submessage_field_name: "field value"})
        """
        message_template = self.value
        
        if target is None:
            target = org.cxsbs.core.clients.AllClientsGroup
        elif isinstance(target, org.cxsbs.core.clients.Client):
            target = Group(org.cxsbs.core.clients.Client, [target])
            
        if not isinstance(target, Group):
            raise Exception()
        
        if not isinstance(speaker, org.cxsbs.core.clients.Client):
            raise Exception()
            
        target = target.query(Select(cn=Compare(127, operator=operator.le))).all()
        
        if len(target.members()) < 1:
            return
        
        message_data = form_message(message_template, fields, submessages)
        
        for client in group.members():
            speaker.sayteam(client.cn, message_data)
    
def MessageDecorator(f):
    '''Decorator which registers a function as an event handler.'''
    message_symbolic_name = f.__module__ + '.' + f.__name__
    message_fields, message_doc = read_message_docstring(f.__doc__)
    message_default_value = f()
    
    message_object = Message(message_symbolic_name, message_fields, message_default_value, message_doc)
            
    return message_object
        

"""
An extremely simple synchronous signal/slot handler system.
"""

class Signal(object):
    def __init__(self):
        self.slots = []
        
    def connect(self, slot):
        if not slot in self.slots:
            self.slots.append(slot)
        
    def disconnect(self, slot):
        if slot in self.slots:
            self.slots.remove(slot)
        
    def emit(self, *args):
        for slot in self.slots:
            slot(*args)

class SignalObject(object):
    def __init__(self):
        "Initialize each attribute signal."
        for key in dir(self):
            val = self.__getattribute__(key)
            if type(val) == type and issubclass(val, Signal):
                self.__setattr__(key, Signal())
        
import unittest

class TestSignals(unittest.TestCase):

    class TestListModel(SignalObject):
    
        update = Signal
    
        def __init__(self):
            SignalObject.__init__(self)
            self.data_list = []

        def add(self, datum):
            self.data_list.append(datum)
            self.update.emit(self.data_list[:])
            
    class TestListView(object):
        def __init__(self, model):
            self.model = model
            self.model.update.connect(self.on_model_update)
            self.data_cache = []
            
        def on_model_update(self, data_list):
            self.data_cache = data_list

    def setUp(self):
        self.test_model = self.TestListModel()
        self.test_view = self.TestListView(self.test_model)

    def test_signals(self):
        self.test_model.add('foo')
        self.assertEqual(self.test_view.data_cache, ['foo'])
        self.test_model.add('bar')
        self.assertEqual(self.test_view.data_cache, ['foo', 'bar'])
        self.test_model.add('baz')
        self.assertEqual(self.test_view.data_cache, ['foo', 'bar', 'baz'])
        
        self.test_model.update.disconnect(self.test_view.on_model_update)
        
        self.test_model.add('zan')
        self.assertEqual(self.test_view.data_cache, ['foo', 'bar', 'baz'])

if __name__ == '__main__':
    unittest.main()

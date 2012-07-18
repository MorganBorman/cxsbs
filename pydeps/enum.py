class enum(object):
    __by_values = {}
    def __init__(self, *items, **kwitems):
        self.__by_values = {}
        
        i = 0
        for item in items:
            self.__by_values[i] = item
            self.__setattr__(item, i)
            i += 1
            
        for item, value in kwitems.items():
            self.__by_values[value] = item
            self.__setattr__(item, value)
            
    def by_value(self, value):
        return self.__by_values[value]
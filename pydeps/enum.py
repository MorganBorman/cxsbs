class enum(object):
    def __init__(self, *items, **kwitems):
        i = 0
        for item in items:
            self.__setattr__(item, i)
            i += 1
            
        for item, value in kwitems.items():
            self.__setattr__(item, value)
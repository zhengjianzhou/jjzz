class Nullable(object):
    '''
    ----------------------------------------------------------------------------------------------------
    The Nullable is designed for avoid NoneType error when calling functions of None-able objects
    --- the idea is the allow the returning wrapped None-able object which can take as many '.' as you
    want. This will allow you to avoid repeated NoneType check. You keep calling the sub functions
    and the wrapper will do the check and return None at the end.
    --- to unwrap the object, simply make a call at the very end to .value()
    
    Sample as below,
    ### call                                 # >>> return
    x = Nullable('Nullable')
    print x.upper().lower().value()          # >>> nullable
    print x.upper().replace('N','M').value() # >>> MULLABLE
    print x.upper().test()                   # >>> <...Nullable object at 0x0000000030B49E10>
    print x.upper()                          # >>> <...Nullable object at 0x0000000030B49E10>
    print x.upper().test().value()           # >>> None
    x = Nullable(None)
    print x.test().value()                   # >>> None
    x = Nullable({1:10, 2:200})
    print x.get(1,0).value()                 # >>> 10
    print x.get(4,{}).value()                # >>> {}
    
    ----------------------------------------------------------------------------------------------------
    '''
    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, attr):
        if self.obj is not None:
            self.attr = attr
            return self
        else:
            return Nullable(None)

    def __call__(self, *args, **kwargs):
        return Nullable(getattr(self.obj, self.attr)(*args,**kwargs)) if \
                self.obj is not None and self.attr is not None and hasattr(self.obj, self.attr) \
            else Nullable(None)
    
    def __getitem__(self, item):
        return Nullable(self.obj[item]) if self.obj and hasattr(self.obj, '__getitem__') else Nullable(None)

    def value(self):
        return self.obj

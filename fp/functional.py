# class definition
class Functional(object):
    def __init__(self, func=None):
        self.funcs = []
        if func != None:
            self.funcs.append(func)

    def __getattr__(self, func):
        if func is not None:
            self.funcs.append(func)
            return self
        else:
            return self

    def __call__(self, *args, **kwargs):
        if args:
            if callable(args[0]):
                self.funcs.append(args[0])
                return self
        return Functional.resolve_fs(*self.funcs)(*args,**kwargs)

    # side effect pass through
    def side_effect(self, func, except_func=None):
        def f(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except:
                try:
                    if except_func:
                        except_func(*args, **kwargs)
                except:
                    pass
            finally:
                return args #, **kwargs)
        self.funcs.append(f)
        return self
    
    @staticmethod
    def resolve_fs(*funcs):
        def fs(_):
            # f is a function takes (k, v) returns (k', v')
            # from copy import deepcopy
            # _ = deepcopy(_)
            for f in funcs[::-1]:
                _ = { x:y for x,y in [f(k,v) for k,v in _.items()]}
            return _
        return fs


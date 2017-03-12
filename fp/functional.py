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
        for a in args:
            if callable(a):
                self.funcs.append(a)
                return self
        return Functional.resolve_fs(*self.funcs)(*args,**kwargs)

    # side effect pass through
    def side_effect(self, func, except_func=None):
        def f(m):
            try:
                func(m)
            except:
                try:
                    if except_func:
                        except_func(m)
                except:
                    pass
            finally:
                return m
        self.funcs.append(f)
        return self
    
    @staticmethod
    def resolve_fs(*funcs):
        def fs(_):
            for f in funcs[::-1]:
                _ = f(_)
            return _
        return fs

def generic(f):
    def gf(m):
        fm = maybe()
        try:
            fm[0] = f(m[0])
        except Exception as e:
            fm[1] = 'generic error: {0}'.format(e)
        return fm
    return gf

class maybe(dict):
    def __init__(self, data=None, state=0):
        super(maybe, self).__init__()
        if data: self[state] = data


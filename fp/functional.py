# Maybe class definition
class Maybe(dict):
    def __init__(self, data=None, state=0):
        super(Maybe, self).__init__()
        if data: self[state] = data

# Functional class definition
class Functional(object):
    def __init__(self, func=None):
        self.funcs = []
        self._add_func_(func)

    def __getattr__(self, func):
        self._add_func_(func)
        return self

    def __call__(self, *args, **kwargs):
        is_func = False
        for a in args:
            if callable(a):
                is_func = True
                self.funcs.append(a)
        if is_func:
            return self
        else:
            return Functional.resolve_fs(*self.funcs)(*args,**kwargs)

    def _add_func_(self, func):
        if func is not None:
            self.funcs.append(generic(func))

    @staticmethod
    def resolve_fs(*funcs):
        def fs(_):
            for f in funcs[::-1]:
                _ = generic(f)(_)
            return _
        return fs

# convert a general function into a function handles Maybe type
def generic(f):
    def gf(m):
        fm = Maybe()
        try:
            fm[0] = f(m[0])
        except Exception as e:
            fm[1] = 'generic error: {0}'.format(e)
        return fm
    return gf

# side effect pass through
def side_effect(func, except_func=None):
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
    return f
    

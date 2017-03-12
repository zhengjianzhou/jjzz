# Maybe class definition
class Maybe(dict):
    def __init__(self, data=None, state=0):
        super(Maybe, self).__init__()
        if data: self[state] = data

# Functional class definition
class Functional(object):
    def __init__(self, auto_lift=True):
        self.auto_lift = auto_lift
        self.funcs = []

    def lift_all(self):
        self.auto_lift = True
        return self

    def unlift_all(self):
        self.auto_lift = False
        return self

    def __getattr__(self, func):
        self._add_func_(func)
        return self

    def __call__(self, *args, **kwargs):
        is_func = False
        for a in args:
            if callable(a):
                is_func = True
                self._add_func_(a)
        if is_func:
            return self
        else:
            return resolve_lifted_fs(*self.funcs)(*args,**kwargs)

    def _add_func_(self, func):
        if func is not None:
            if self.auto_lift:
                self.funcs.append(lift(func))
            else:
                self.funcs.append(func)

def resolve_lifted_fs(*funcs):
    def fs(_):
        for f in funcs[::-1]:
            _ = f(_)
        return _
    return fs

def lift_n_resolve_fs(*funcs):
    return resolve_lifted_fs(*[lift(f) for f in funcs])

# lift a general function into a composible function handles Maybe type
def lift(f):
    def gf(m):
        fm = Maybe()
        try:
            fm[0] = f(m[0])
        except Exception as e:
            fm[1] = 'lifting error: {0}'.format(e)
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


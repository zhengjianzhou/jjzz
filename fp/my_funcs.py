# function definition
import math
from functional import Maybe

sq    = lambda x:x*x
cube  = lambda x:x*x*x
minus = lambda x:-x
rt    = lambda x:math.sqrt(x)

def rt_m(m):
    if m.has_key(1):
        return Maybe('|=> error from org {0}'.format(m), 1)
    else:
        if m.has_key(0) and m[0] >=0:
            return Maybe(math.sqrt(m[0]))
        else:
            return Maybe('|=> error square root on a minus number: {0}'.format(m[0]), 1)


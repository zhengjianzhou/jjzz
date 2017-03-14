# function definition
import math
from maybe import Maybe

sq    = lambda x:x*x
cube  = lambda x:x*x*x
minus = lambda x:-x
rt    = lambda x:math.sqrt(x)

def rt_m(m):
    if m.state:
        return m
    else:
        if m.state == 0 and m.data >=0:
            return Maybe(math.sqrt(m.data))
        else:
            return Maybe('|=> error sqrt on a minus: {0}'.format(m), 1)


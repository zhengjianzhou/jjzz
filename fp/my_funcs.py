# function definition
import math
def sq(k,v):
    # print k,v
    return (k, v*v) if k==0 else (1, '|=> sq error: from org {0}'.format(v))

def cube(k,v):
    # print k,v
    return (k, v*v*v) if k==0 else (1, '|=> cube error: from org {0}'.format(v))

def rt(k,v):
    # print k,v
    return (0, math.sqrt(v)) if k==0 and v>=0 else (1,'|=> rt error:sqrt on minus')

def minus(k,v):
    # print k,v
    return (0, -v) if k==0 else (1,'|=> minus error: from org {0}'.format(v))


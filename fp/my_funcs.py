# function definition
import math
from functional import generic,maybe

def sq(m):
    return generic(lambda x:x*x) (m)

def cube(m):
    return generic(lambda x:x*x*x) (m)

def rt(m):
    return maybe(math.sqrt(m[0])) if m.has_key(0) and m[0]>=0 else maybe('|=> rt error:sqrt on minus',1)

def minus(m):
    return generic(lambda x:-x) (m)


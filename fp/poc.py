#!/usr/bin/python
from functional import Functional,generic,maybe
from data import DATA_Num, DATA_Str, DATA_List
from my_funcs import *

DATA_1 = maybe(DATA_Num)
print '--------traditional--------'
run_f = Functional.resolve_fs(*[sq,cube,rt])
print run_f (DATA_1)
print '---------------------------'

print '--------functional---------'
print Functional()(sq)(DATA_1)
print '---------------------------'

print '--------functional-break---'
print Functional()(cube)(rt)(cube)(DATA_1)
print '---------------------------'

print '--------functional-generic-'
print Functional()(cube)(generic(lambda x:x*x))(generic(lambda x:x-1))(DATA_1)
print '---------------------------'

print '--------side effect--------'
def print_state(*a): print a
print Functional()(rt).side_effect(print_state)(minus)(sq).side_effect(print_state)(cube)(DATA_1)
print '---------------------------'

DATA_2 = maybe(DATA_Str)
print '--------functional-generic-'
print Functional()(generic(lambda x:x+'!'))(generic(lambda x:'Hello '+x))(DATA_2)
print '---------------------------'

DATA_3 = maybe(DATA_List)
print '--------functional-generic-'
print Functional()(generic(lambda x:len(x))).side_effect(print_state)(generic(lambda x:x*2))(DATA_3)
print '---------------------------'


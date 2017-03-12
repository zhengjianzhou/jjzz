#!/usr/bin/python
from functional import Functional,Maybe,side_effect
from data import DATA_Num, DATA_Str, DATA_List
from my_funcs import *

DATA_1 = Maybe(DATA_Num)
print '--------traditional--------'
run_f = Functional.resolve_fs(*[sq,rt,sq,cube])
#run_f = Functional.resolve_fs(*[sq,cube,rt])
print run_f (DATA_1)
print '---------------------------'

print '--------functional---------'
print Functional()(sq)(DATA_1)
print '---------------------------'

print '--------functional-break---'
print Functional()(cube)(rt)(cube)(DATA_1)
print '---------------------------'

print '--------functional-generic-'
print Functional()(cube)(lambda x:x*x)(lambda x:x-1)(DATA_1)
print '---------------------------'

def print_state(a): print '\=> SIDE EFFECT: ', a
print '--------side effect--------'
print Functional()(rt)(side_effect(print_state))(minus)(sq)(side_effect(print_state))(cube)(DATA_1)
print '---------------------------'

DATA_2 = Maybe(DATA_Str)
print '--------functional-generic-'
print Functional()(lambda x:x+'!')(lambda x:'Hello '+x)(DATA_2)
print '---------------------------'

DATA_3 = Maybe(DATA_List)
print '--------functional-generic-'
print Functional()(lambda x:len(x))(side_effect(print_state))(lambda x:x*2)(DATA_3)
print '---------------------------'


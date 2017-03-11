from functional import Functional
from data import DATA_DICT_1
from my_funcs import *

print '--------traditional--------'
run_f = Functional.resolve_fs(*[sq,cube,rt])
print run_f (DATA_DICT_1)

print '--------functional---------'
print Functional()(sq)(DATA_DICT_1)

print '--------functional-break---'
print Functional()(cube)(rt)(cube)(DATA_DICT_1)

print '--------side effect--------'
def s(*a): print a
print Functional()(rt).side_effect(s)(minus)(sq).side_effect(s)(cube)(DATA_DICT_1)



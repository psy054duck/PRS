from z3 import *

s = Solver()

f = Function('f', IntSort(), IntSort())
n = Int('n')


res = s.check(ForAll(n, f(n) == If(n > 0, n+1, n)))
print(res)
print(s.model())
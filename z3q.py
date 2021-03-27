from z3 import *
n = Int("n")
N = Int("N")
s = set()
s.add(N >= 0)
solver = Solver()
x1 = Int("x1")
x2 = Int("x2")
i1 = Int("i1")
i2 = Int("i2")
i3 = Function("i3", IntSort(), IntSort())
i4 = Int("i4")
sn1 = Int("sn1")
sn2 = Function("sn2", IntSort(), IntSort())
sn3 = Int("sn3")
i0 = Int("i0")
s.add(i1 == i0)
s.add(x2 == x1)
s.add(sn1 == 0)
s.add(i2 == 0)
s.add(sn2(0) == sn1)
s.add(ForAll(n, Implies(n >= 0, sn2(n + 1) == If(i3(n) == 4, -10, sn2(n) + 2))))
########## closed form ##########
s.add(ForAll(n, Implies(n >= 0, sn2(n) == If(And(0 <= n, n < 4), 2*n, If(And(4 <= n, n < 5), -10, 2*n - 20)))))
#################################
s.add(sn3 == sn2(N))
s.add(i3(0) == i2)
s.add(ForAll(n, Implies(n >= 0, i3(n + 1) == If(i3(n) == 4, i3(n) + 1, i3(n) + 1))))
########## closed form ##########
s.add(ForAll(n, Implies(n >= 0, i3(n) == If(And(0 <= n, n < 4), n, If(And(4 <= n, n < 5), n, n)))))
#################################
s.add(i4 == i3(N))
s.add(ForAll(n, Implies(And(0 <= n, n < N), i3(n) < x2)))
s.add(Not(i3(N) < x2))
########## assert ##########
# s.add(Not(sn3 == 2*x2))
############################
def query():
    return solver.check(s)

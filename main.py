from PRS import solve
import os
import sympy as sp
import time

for dirpath, _, filenames in os.walk('benchmarks/support'):
    for filename in filenames:
        try:
            print('processing %s' % filename, end=': ')
            path = os.path.join(dirpath, filename)
            start = time.time()
            res = solve(path)
            print('%.4f ' % res[-1], end='')
            if res is not None:
                print('%s: success' % path)
            else:
                print('%s: fail' % path)
        except:
            print('parsing error')
# n = sp.Symbol('n')
# m = sp.Matrix([[0, 0, 0], [0, 1, 1], [0, 0, 1]])
# # print(m.eigenvals())
# print(m**n)
# m = sp.Matrix([[1, 1], [0, 1]])
# eigenval = m.eigenvals()
# print(eigenval)
# print(m.jordan_block(eigenvalue=1, size=2))
# print(m**n)
# res = solve('benchmarks/recurrence/conditional/test5')
# print(res)
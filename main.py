from PRS import solve
import os
import sympy as sp
import time
from cparser import check

check('benchmarks/experiment/loops-crafted-1/mono-crafted_6.c')
# check('benchmarks/experiment/loops/sum01_bug02_sum01_bug02_base.case.c')
# check('test.c')

# for dirpath, _, filenames in os.walk('benchmarks/support'):
#     for filename in filenames:
#         try:
#             print('processing %s' % filename, end=': ')
#             path = os.path.join(dirpath, filename)
#             start = time.time()
#             res = solve(path)
#             print('%.4f ' % res[-1], end='')
#             if res is not None:
#                 print('%s: success' % path)
#             else:
#                 print('%s: fail' % path)
#         except:
#             print('parsing error')
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
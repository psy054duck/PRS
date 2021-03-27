import sympy as sp
from .condition import And, PolyCondition, ModCondition
from .closed_form import closed_form
from .parser import parse
import os
import time

def solve(filename):
    with open(filename) as fp:
        recurrence = fp.read()
        res = solve_str(recurrence)
        return res


def solve_str(recurrence: str):
    cond, x0, A, variables, index = parse(recurrence)
    start = time.time()
    res = closed_form(A, x0, cond, variables, index)
    # print(sp.expand(res[1][0].subs(index, 5)))
    # for i in range(6, 12):
    #     print(sp.expand(res[1][1].subs(index, i)))
    end = time.time()
    if res is None:
        return None
    return res, variables, index, end - start

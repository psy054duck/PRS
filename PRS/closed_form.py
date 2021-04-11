import sympy as sp
import functools
from .guess import guess_pattern
from .utils import my_expand, my_simplify, next_element
from .validation import validate
from .condition import PolyCondition

def jordan_cell_power(jc, n):
        N = jc.shape[0]
        l = jc[0, 0]
        for i in range(N):
                for j in range(N-i):
                        bn = sp.binomial(n, i)
                        if isinstance(bn, sp.binomial):
                                bn = bn._eval_expand_func()
                        jc[j, i+j] = l**(n-i)*bn if l != 0 else 0


def matrix_power(M, n):
        P, jordan_cells = M.jordan_cells()
        for j in jordan_cells:
                jordan_cell_power(j, n)
        a = P
        b = sp.diag(*jordan_cells)
        c = P.inv()
        return P*sp.diag(*jordan_cells)*P.inv()

def closed_form(A, x0, conds, order, n, bnd=100):
    rename = {order[i]: sp.Symbol('_PRS_x%d' % i) for i in range(len(order))}
    conds = [cond.subs(rename) for cond in conds]
    a = 1
    cs = [0]
    closed_forms = []
    start = True
    while a < bnd + 1:
        print(x0)
        a += 1
        c, xc, pattern, others = guess_pattern(A, x0, conds, 2*a)
        if pattern is None: continue
        if c != 0:
            res = _closed_form(A, x0, others, n)
            res = res.applyfunc(functools.partial(my_simplify, n=n))
            if res.subs(n, 0) != x0:
                cs.append(cs[-1] + 1)
                closed_forms.append(x0)
                res = res.subs(n, n + 1)
            closed_forms.append(res.subs(n, n - cs[-1]))
            cs.append(cs[-1] + c - 1)

        res = _closed_form(A, xc, pattern, n)
        res = res.applyfunc(functools.partial(my_simplify, n=n))
        if res.subs(n, 0) != xc:
            cs.append(cs[-1] + 1)
            closed_forms.append(xc)
            res = res.subs(n, n + 1)
        res_validate = validate(res, conds, pattern, n)
        closed_forms.append(res.subs(n, n - cs[-1]))
        if all(p[0] for p in res_validate):
            return cs, closed_forms
        else:
            start = min(p[1] for p in res_validate if not p[0]) - 1
            x0 = res.subs(n, start)
            # x0 = res.subs(n, cs[-1] + start)
            x0 = next_element(A, x0, conds)
            cs.append(cs[-1] + start + 1)
        # if j == 0:
        #     res = _closed_form(A, xj, pattern, n)
        #     res_validate = validate(res, conds, pattern, n)
        #     res = res.applyfunc(functools.partial(my_simplify, n=n))
        # else:
        #     res = _closed_form(A, x0, others, n)
        #     res = res.applyfunc(functools.partial(my_simplify, n=n))
        #     js.append(js[-1] + j)
        #     closed_forms.append(res)

        #     res = _closed_form(A, xj, pattern, n)
        #     res_validate = validate(res, conds, pattern, n)
        #     res = res.applyfunc(functools.partial(my_simplify, n=n))

        # if j == 0:
        #     res = _closed_form(A, xj, pattern, n)
        #     res_validate = validate(res, conds, pattern, n)
        #     res = res.applyfunc(functools.partial(my_simplify, n=n))
        #     closed_forms.append(res)
        # else:
        # res = _closed_form(A, xj, pattern, n)
        # original_res = res
        # if j != 0:
        #     start_res = _closed_form(A, x0, others, n)
        #     if start:
        #         start_res = start_res.subs(n, n - js[-1])
        #     else:
        #         start_res = start_res.subs(n, n - js[-1] + 1)
        #     if start_res.subs(n, 0) != x0 and start:
        #         js.append(j + js[-1])
        #         closed_forms.append(x0)
        #     closed_forms.append(start_res)
        #     js.append(j + js[-1])
        # print('*'*10)
        # print(js)
        # print(xj)
        # print(res)
        # print(res.subs(n, n - js[-1]))
    #     res_validate = validate(original_res, conds, pattern, n)
    #     res = res.applyfunc(functools.partial(my_simplify, n=n))
    #     if res.subs(n, 0) != xj and start:
    #         closed_forms.append(xj)
    #         res = res.subs(n, n - js[-1])
    #         js.append(1 + js[-1])
    #     elif start:
    #         res = res.subs(n, n - js[-1])
    #     else:
    #         res = res.subs(n, n - js[-1] + 1)
    #     closed_forms.append(res)

    #     if all(p[0] for p in res_validate):
    #         return js, closed_forms
    #     else:
    #         start = min(p[1] for p in res_validate if not p[0]) + js[-1]
    #         x0 = res.subs(n, start)
    #         # a = 1
    #         js.append(start)
    #         start = False
    # else:
    #     return None

def _closed_form(A, x0, pattern, n):
    dim = A[0].shape[0]
    num = len(pattern)
    s = _selector(num, n)
    S = sp.Matrix([[s.subs(n, n+i)*sp.eye(dim) for i in range(num, 0, -1)]])
    m = _rearrange_matrix(A, pattern)
    extended_x0 = x0.row_insert(len(x0), sp.zeros(dim*(num - 1), 1))
    res = S*matrix_power(m, n)*extended_x0
    res = sp.powsimp(res, force=True)
    res = sp.simplify(res, force=True)
    return res

def _selector(k, n):
    '''Compute the closed form for sequence defined by
f(0) = 1,
f(1) = ... = f(k-1) = 0,
f(n+k) = f(n)'''
    f = sp.Function('f')
    inits = {f(0): 1}
    inits.update({f(i): 0 for i in range(1, k)})
    return sp.rsolve(f(n+k) - f(n), f(n), inits)

def _rearrange_matrix(A, pattern):
    dim = A[0].shape[0]
    num = len(pattern)
    m = sp.Matrix([[sp.zeros(dim)]*(num - 1) + [A[pattern[0]]]])
    pattern = list(reversed(pattern))
    for i in range(num-1):
        l = [sp.zeros(dim)]*i + [A[pattern[i]]] + [sp.zeros(dim)]*(num - i - 1)
        m = m.row_insert(m.shape[0], sp.Matrix([l]))
    return m


if __name__ == '__main__':
    # A, x0, v = generate_instance(num_var=2, num_pieces=3, seed=None)
    A = [sp.Matrix([[1, 2], [-1, 4]]),
         sp.Matrix([[3, 5], [-sp.Rational(6, 5), 8]]),
         sp.Matrix([[70, 3], [141, 7]])]
    A = [sp.Matrix([[1, 0, 1], [0, -1, 0], [0, 0, 1]]), sp.Matrix([[1, 0, 2], [0, -1, 0], [0, 0, 1]])]
    x0 = sp.Matrix([[0], [1], [1]])
    v = [sp.Matrix([[0, 1, 0]])]
    # A = [sp.Matrix([[-4, 0, 0, 0], [66, -28, -66, 24], [-33, 12, 29, -12], [78, -33, -78, 29]])]
    # x0 = sp.Matrix([[1], [1], [1], [1]])
    # v = [sp.Matrix([[0], [0], [0], [0]])]
    # j, xj, pattern = guess_pattern(A, x0, v, 10)
    # print(j, pattern)
    # m = _rearrange_matrix(A, pattern)
    n = sp.Symbol('n')
    x1, x2, x3 = sp.symbols('x1 x2 x3')
    j, xj, close = closed_form(A, x0, [PolyCondition(x2)], [x1, x2, x3], n, 6)
    print(close)
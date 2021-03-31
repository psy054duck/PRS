import sympy as sp
from .validation import ep_ge_0
from .utils import to_exponential_polynomial, my_simplify

class Condition:
    def __init__(self, cond):
        self.cond = cond

    def evaluate(self, values):
        return self.cond.subs(values, simultaneous=True)

    def subs(self, mapping):
        return Condition(self.cond.subs(mapping, simultaneous=True))

    def validate(self, t, f, k, n, closed_form):
        to_validated = self.cond.subs({sp.Symbol('_PRS_x%d' % i): closed_form[i] for i in range(closed_form.shape[0])}, simultaneous=True)
        for i in t:
            check = to_validated.subs(n, k*n + i)
            if sp.simplify(check) != True:
                return False
        for i in f:
            check = to_validated.subs(n, k*n + i)
            if sp.simplify(check) == True:
                return False
        return True

class TrueCondition(Condition):
    def evaluate(self, values):
        return True

    def validate(self, t, f, k, n, closed_form):
        return [(True, -1)] * (len(t) + len(f))

    def subs(self, mapping):
        return self

class And(Condition):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def evaluate(self, values):
        res = self.lhs.evaluate(values) and self.rhs.evaluate(values)
        return res

    def validate(self, t, f, k, n, closed_form):
        # print('*'*10)
        # print(t)
        # print(f)
        res_lhs = self.lhs.validate(t, f, k, n, closed_form)
        res_rhs = self.rhs.validate(t, f, k, n, closed_form)
        # print(res_lhs, self.lhs)
        # print(res_rhs, self.rhs)
        res = []
        for _ in t:
            for l, r in zip(res_lhs[:len(t)], res_rhs[:len(t)]):
                if l[0] and r[0]:
                    res.append((True, -1))
                elif not l[0] and r[0]:
                    res.append((False, l[1]))
                elif l[0] and not r[0]:
                    res.append((False, r[1]))
                else:
                    res.append((False, min(l[1], r[1])))
        for _ in f:
            for l, r in zip(res_lhs[len(t):], res_rhs[len(t):]):
                if l[0] or r[0]:
                    res.append((True, -1))
                else:
                    res.append((False, max(l[1], r[1])))
        # return self.lhs.validate(t, f, k, n, closed_form) and self.rhs.validate(t, f, k, n, closed_form)
        return res

    def subs(self, mapping):
        return And(self.lhs.subs(mapping), self.rhs.subs(mapping))

class PolyCondition(Condition):
    def __init__(self, cond, strict=False):
        super().__init__(cond)
        self.strict = strict

    def __repr__(self):
        return 'PolyCondition(%r, strict=%r)' % (self.cond, self.strict)

    def subs(self, mapping):
        return PolyCondition(self.cond.subs(mapping, simultaneous=True), strict=self.strict)

    def evaluate(self, values):
        v = self.cond.subs(values, simultaneous=True)
        return v > 0 if self.strict else v >= 0

    def validate(self, t, f, k, n, closed_form):
        to_validated = self.cond.subs({sp.Symbol('_PRS_x%d' % i): closed_form[i] for i in range(closed_form.shape[0])}, simultaneous=True)
        res = []
        for i in t:
            e = to_validated.subs(n, k*n + i)
            res_validate = ep_ge_0(e, n, strict=self.strict)
            res.append((res_validate[0], res_validate[1]*k + i))
        for i in f:
            e = -to_validated.subs(n, k*n + i)
            res_validate = ep_ge_0(e, n, strict=(not self.strict))
            res.append((res_validate[0], res_validate[1]*k + i))
        return res

class ModCondition(Condition):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def subs(self, mapping):
        return ModCondition(self.lhs.subs(mapping, simultaneous=True), self.rhs)

    def evaluate(self, values):
        return sp.simplify(self.lhs.subs(values, simultaneous=True) % self.rhs) == 0

    def validate(self, t, f, k, n, closed_form):
        to_validated = self.lhs.subs({sp.Symbol('_PRS_x%d' % i): closed_form[i] for i in range(closed_form.shape[0])}, simultaneous=True)
        res = []
        for i in t:
            check = my_simplify(to_validated.subs(n, k*n + i), n)
            if sp.Eq(check % self.rhs, 0) != True:
                for x in range(999999999999):
                    if sp.Eq(check % self.rhs, 0) != True:
                        res.append((False, x*k + i))
                        break
            else:
                res.append((True, -1))
        for i in f:
            check = my_simplify(to_validated.subs(n, k*n + i), n)
            # print(check)
            if sp.Eq(check % self.rhs, 0):
                for x in range(999999999999):
                    if sp.Eq(check % self.rhs, 0):
                        res.append((False, x*k + i))
                        break
            else:
                res.append((True, -1))
        return res

if __name__ == '__main__':
    x1, x2 = sp.symbols('x1 x2')
    cond = PolyCondition(sp.Ge(x1 + x2, 1))
    print(cond.evaluate({x1: 10, x2: -20}))
import sympy as sp
from importlib import reload

import signal
import time
  
  
def set_timeout(num, callback):
  def wrap(func):
    def handle(signum, frame):
      raise RuntimeError
  
    def to_do(*args, **kwargs):
      try:
        signal.signal(signal.SIGALRM, handle)
        signal.alarm(num)
        r = func(*args, **kwargs)
        signal.alarm(0)
        return r
      except RuntimeError as e:
        callback()
  
    return to_do
  
  return wrap

def to_PRS(inits, recurrence):
    res = ''.join('%s = %s;\n' % (var, inits[var]) for var in inits) + '\n'
    conds = {}
    # print(recurrence[0][0])
    if recurrence[1][0] == True:
        body = ''.join('%s = %s;\n' % (var, recurrence[0][0][var]) for var in recurrence[0][0])
        res += r'if (true) {%s}' % body
    else:
        for body, cond in zip(*recurrence):
            if isinstance(cond, sp.Eq):
                if isinstance(cond.lhs, sp.Mod):
                    res += 'if (%s) {\n%s} else ' % ('%s %% %s == %s' % (cond.lhs.args[0], cond.lhs.args[1], cond.rhs), dict2c(body))
                else:
                    res += 'if (%s) {\n%s} else ' % ('%s == %s' % (cond.lhs, cond.rhs), dict2c(body))
            else:
                res += 'if (%s) {\n%s} else ' % (cond, dict2c(body))
        res += '{\n%s}' % dict2c(recurrence[0][-1])
    return res

def dict2c(d):
    return ''.join('%s = %s;\n' % (k, d[k]) for k in d)

def z3query(query):
    with open('z3q.py', 'w') as fp:
        fp.write(query)
        fp.write('def query():\n')
        fp.write('    return solver.check(s)\n')
    import z3q as q
    q = reload(q)
    return q.query()
    

def closed_form2z3(closed_form, order, var, index):
    conds, closed = closed_form[0], closed_form[1]
    closed_form_index = order.index(var)
    res = 'If(%s, %s, %s)'
    for i in range(len(conds)-1):
        cond_str = 'And(%s <= %s, %s < %s)' % (conds[i], index, index, conds[i+1])
        if i < len(conds) - 2:
            res = res % (cond_str, closed[i][closed_form_index], 'If(%s, %s, %s)')
        else:
            res = res % (cond_str, closed[i][closed_form_index], '%s')
    if len(conds) == 1:
        res = closed[0][closed_form_index]
    else:
        res = res % closed[-1][closed_form_index]
    return res
        # res = res % ('And(%s <= %s, %s <  %s)' % (conds[i]))

def analyze_loop(loop_guard, loop_body):
    assignments = [[{}, {}], [sp.true]]
    for statement in loop_body:
        if is_assignment(statement):
            lhs = get_assignment_lhs(statement)
            rhs = get_assignment_rhs(statement)
            for branch in assignments[0]:
                updated = rhs.subs(branch, simultaneous=True)
                branch[lhs] = updated
        elif is_selection(statement):
            if assignments[1][0]:
                values = assignments[0][0]
                bodies_conds = selection_bodies_conds(statement)
                new_bodies = []
                new_conds = []
                for seq_body in bodies_conds[0]:
                    body = sequence2parallel(seq_body)
                    for var in body:
                        body[var] = body[var].subs(values)
                    for var in values:
                        if var not in body:
                            body[var] = values[var]
                    new_bodies.append(body)
                for i, cond in enumerate(bodies_conds[1]):
                    new_conds.append(cond.subs(values))
                assignments = new_bodies, new_conds
            else:
                raise Exception('Only one sequence of if-else is supported now')
    involved_variables = set()
    for body in assignments[0]:
        for var in body:
            involved_variables.add(var)
    for body in assignments[0]:
        for var in involved_variables:
            if var not in body:
                body[var] = var

    return ('iteration', assignments, loop_guard)

def is_assignment(statement):
    return statement[0] == 'assignment'

def is_assignment_list(statement):
    return statement[0][0] == 'assignment'

def is_iteration(statement):
    return statement[0] == 'iteration'

def is_for_iteration(statement):
    return statement[0] == 'for-iteration'

def is_selection(statement):
    return statement[0] == 'selection'

def is_function_call(statement):
    return statement[0] == 'call'

def function_name_args(statement):
    if len(statement) > 2:
        return statement[1], statement[2:]
    else:
        return (statement[1],)

def relation2str(relation):
    if isinstance(relation, sp.Eq):
        return '%s == %s' % (relation2str(relation.lhs), relation2str(relation.rhs))
    elif isinstance(relation, sp.Ne):
        return '%s != %s' % (relation2str(relation.lhs), relation2str(relation.rhs))
    elif isinstance(relation, sp.Or):
        return 'Or(%s, %s)' % (relation2str(relation.args[0]), relation2str(relation.args[1]))
    elif isinstance(relation, sp.And):
        return 'And(%s, %s)' % (relation2str(relation.args[0]), relation2str(relation.args[1]))
    else:
        return str(relation)

def assignment2dict(assignment):
    return {assignment[1]: assignment[2]}

def get_assignment_lhs(assignment):
    return assignment[1]

def get_assignment_rhs(assignment):
    return assignment[2]

def create_assignment(lhs, rhs):
    return ('assignment', lhs, rhs)

def selection_bodies_conds(selection):
    if selection[2][0] != 'selection':
        return [selection[1], selection[2]], [selection[3]]
    else_branch = selection_bodies_conds(selection[2])
    return [selection[1]] + else_branch[0], [selection[3]] + else_branch[1]

def sequence2parallel(sequence):
    values = {}
    for i, statement in enumerate(sequence):
        lhs = get_assignment_lhs(statement)
        rhs = get_assignment_rhs(statement)
        rhs = rhs.subs(values, simultaneous=True)
        values[lhs] = rhs
    return values

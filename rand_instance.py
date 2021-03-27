import sympy as sp

_min, _max = -10, 10
def generate_linear_instance(num_var, num_pieces, seed=None):
    A = [sp.randMatrix(num_var, min=_min, max=_max, seed=seed) for _ in range(num_pieces)]
    v = [sp.randMatrix(num_var, c=1, min=_min, max=_max, seed=seed) for _ in range(num_pieces - 1)]
    x = sp.randMatrix(num_var, c=1, min=_min, max=_max, seed=seed)
    return A, x, v

if __name__ == '__main__':
    A, x, v = generate_linear_instance(2, 3, seed=100)
    print(A)
    print(x)
    print(v)

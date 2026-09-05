# linprog(c) raises misleading `ValueError: must give A and B` instead of UnboundedLPError when called without A and b

when run
```python
from sympy.solvers.simplex import linprog
linprog([-1])
```
Output:--
```python
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
Cell In[3], line 2
      1 from sympy.solvers.simplex import linprog
----> 2 linprog([-1])

File /lib/python3.13/site-packages/sympy/solvers/simplex.py:1046, in linprog(c, A, b, A_eq, b_eq, bounds)
   1043 else:
   1044     aux = -A.cols  # set so -aux will give all cols below
-> 1046 o, p, d = _simplex(A, b, C)
   1047 return o, p[:-aux]

File /lib/python3.13/site-packages/sympy/solvers/simplex.py:279, in _simplex(A, B, C, D, dual)
    277 else:
    278     if A or B:
--> 279         raise ValueError("must give A and B")
    280     # no constraints given
    281     M = Matrix([[C, D]])

ValueError: must give A and B
```

Tested on:- sympy==1.14.0

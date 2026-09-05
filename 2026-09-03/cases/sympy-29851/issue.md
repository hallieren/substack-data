# `z3_satisfiable` gives wrong ans

```python
from sympy.logic.algorithms.z3_wrapper import z3_satisfiable
from sympy.assumptions import Q
from sympy.logic.boolalg import Not , Implies

x = symbols('x')
res = z3_satisfiable(Not(Implies(Q.eq(x, 0), Q.ge(x, 0))))
print(f"Satisfiable: {res}")  
# Satisfiable: {Q.gt(x, 0): False, Q.eq(x, 0): True}
```

$¬(x=0⇒x≥0)$
$¬(x=0⇒x≥0)≡(x=0)∧¬(x≥0)≡(x=0)∧(x<0)$
$(x=0)∧(x<0)≡⊥$

The problem is unsat but `z3_satisfiable` gives a solution `{Q.gt(x, 0): False, Q.eq(x, 0): True}`

Py version: Python 3.14.4
OS: Ubuntu 24.04.3
Version of sympy: Master branch of sympy (1.15.0.dev0)

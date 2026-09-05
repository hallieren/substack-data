# Bug of DMP diff

Code:
```
from sympy import *
from sympy.abc import x, y, z
p = Poly(x**7*y**5 + 2*x**7*y**4 + x**2,x,y,z,modulus=7)
print(p.diff().expr.as_poly(x, y, z, modulus=7).gcd(p))
print(p.diff().rep.to_list())
print(p.diff().gcd(p))
```

The outputs are:
```
Poly(x, x, y, z, modulus=7)
[[[], [], [], [], [], []], [[]], [[]], [[]], [[]], [[2]], [[]]]
Traceback (most recent call last):
```
(and the last line raises ZeroDivisionError).

It seems to be a bug in `dmp_diff_in` for FiniteFields.

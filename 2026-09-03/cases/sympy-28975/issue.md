# problem with `limit(2**(1/x), x, 0, dir='-')` and `sp.limit(2**x, x, -sp.oo)`

Could someone help me with this issue in sympy 1.13.3? I'm expecting the left limit to be 0.
```
>>> import sympy as sp
>>> x = sp.symbols('x')
>>> sp.limit(2**(1/x), x, 0, dir='-')
oo
```
I tried a simplified version, and got the same error
```
>>> sp.limit(2**x, x, -sp.oo)
oo
```

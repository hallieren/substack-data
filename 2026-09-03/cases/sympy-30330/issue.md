# subresultants_pg / modified_subresultants_pg crash with TypeError: Invalid NaN comparison when q | p

Reading the subresultant implementations in \`sympy.polys.subresultants_qq_zz\` while auditing them against \`polytools.subresultants\`, I found that the Pell-Gordon (pg) variants crash whenever a pseudo-remainder is identically zero.

\`\`\`python
>>> from sympy import symbols, Rational
>>> from sympy.polys.subresultants_qq_zz import (
...     subresultants_pg, modified_subresultants_pg)
>>> x = symbols('x')
>>> p = 4*x**3 + 3*x**2 + x + 2
>>> q = x + 1
>>> p.subs(x, -1)
0                                   # q | p
>>> subresultants_pg(p, q, x)
Traceback (most recent call call):
...
TypeError: Invalid NaN comparison
>>> modified_subresultants_pg(p, q, x)   # same crash
TypeError: Invalid NaN comparison
\`\`\`

Present in 1.14.0 and current master.

## Root cause

In \`modified_subresultants_pg\`, when the first pseudo-remainder is zero (\`q | p\`):

1. \`a2 = -rem(p, q) = 0\`,
2. \`d2 = degree(0, x) = -oo\`, so \`deg_diff_new = exp_deg - d2 = oo\`,
3. \`deg_diff_new == 0\` is False → the *incomplete sequence* branch builds

   \`\`\`
   den = den * rho_list[len(rho_list)-1]**expo
   \`\`\`

   with \`expo\` involving \`oo\`; since every \`rho_list\` entry is ±1 and \`(-1)**oo == nan\` in SymPy, \`den\` becomes \`nan\`,
4. line 1467 (master)

   \`\`\`python
   if sign(num / den) > 0:
   \`\`\`

   evaluates \`sign(nan)\` and \`StrictGreaterThan(S.NaN, 0)\` raises \`TypeError: Invalid NaN comparison\`.

The trailing cleanup anticipates this case —

\`\`\`python
if subres_l[m - 1] == nan or subres_l[m - 1] == 0:
    subres_l.pop(m - 1)
\`\`\`

— but \`Expr.__eq__(nan)\` is always False, so it can never fire. (This \`x == nan\` pattern occurs 8 times in the module and is separately dead code.)

The same crash also happens when the sequence terminates later: \`subresultants_pg(x**4 - 1, x**2 - 1, x)\`.

## Expected behaviour

Match \`sympy.polys.polytools.subresultants\`, which handles common roots fine:

\`\`\`python
>>> from sympy import subresultants
>>> subresultants(p, q, x)
[4*x**3 + 3*x**2 + x + 2, x + 1]
\`\`\`

i.e. a zero remainder must simply terminate the sequence.

I have a fix ready (skip the Pell-Gordon updates on a zero remainder in both the first-remainder step and the main loop) — PR to follow.


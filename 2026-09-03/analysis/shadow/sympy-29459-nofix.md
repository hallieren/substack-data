# sympy-29459-nofix — https://github.com/sympy/sympy/issues/29459

## reference

F2P: []

pico's F2P results: {}

## pico's final report

## Summary

The issue was in `generate_lambda_lookup` in `sympy/polys/numberfields/galois_resolvents.py`, which builds a large Python source string for the `resolvent_lookup.py` table. Two inefficiencies were fixed:

1. **List comprehension → generator expression** for `lambda_lists[k]`: the intermediate list holding all per-coefficient strings was eliminated; `str.join` now consumes the generator directly, saving memory.

2. **Repeated `table += ...` string concatenation → single `str.join`**: the loop that appended each resolvent entry with repeated in-place string concatenation (quadratic copying of the growing immutable string) was replaced by building all entries at once with `''.join(generator)`, giving O(n) construction and eliminating the intermediate per-line strings.

Both changes preserve byte-for-byte output (verified against the original implementation by diffing trial-run output; only the inherently run-dependent timing comment lines differ). The module compiles and the existing `test_galoisgroups.py` suite passes (8 passed).

## pico's patch

```diff
diff --git a/sympy/polys/numberfields/galois_resolvents.py b/sympy/polys/numberfields/galois_resolvents.py
index ab71e85cf2..0faf88bdb5 100644
--- a/sympy/polys/numberfields/galois_resolvents.py
+++ b/sympy/polys/numberfields/galois_resolvents.py
@@ -613,10 +613,10 @@ def generate_lambda_lookup(verbose=False, trial_run=False):
 
         sv = s_vars(len(X))
         head = f'lambda {", ".join(str(v) for v in sv)}:'
-        lambda_lists[k] = ',\n        '.join([
+        lambda_lists[k] = ',\n        '.join(
             f'{head} ({wrap(f)})'
             for f in symmetrized
-        ])
+        )
 
         if trial_run:
             break
@@ -629,10 +629,10 @@ def generate_lambda_lookup(verbose=False, trial_run=False):
         f"# The final polynomial of Case (6, 1) alone took {time_for_61_last:.2f}s.\n"
          "resolvent_coeff_lambdas = {\n")
 
-    for k, L in lambda_lists.items():
-        table += f"    {k}: [\n"
-        table +=  "        " + L + '\n'
-        table +=  "    ],\n"
+    table += ''.join(
+        f"    {k}: [\n        {L}\n    ],\n"
+        for k, L in lambda_lists.items()
+    )
     table += "}\n"
     return table
 

```

## human fix (merged PR #None)

```diff

```

## maintainers' ruling

[jonathandung 2026-03-26] The PR was closed, so I will close this issue.


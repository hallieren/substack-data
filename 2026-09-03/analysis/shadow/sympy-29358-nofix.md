# sympy-29358-nofix — https://github.com/sympy/sympy/issues/29358

## reference

F2P: []

pico's F2P results: {}

## pico's final report

Implemented the fix by undoing the regressions introduced by PR #27492 in the source files:

- `sympy/assumptions/facts.py`
  - Restored `get_composite_predicates()`.
  - Removed the explicit `Equivalent(..., ...)` clauses for composite predicates from `get_number_facts()`.
  - `get_known_facts()` now again has 52 arguments.

- `sympy/assumptions/cnf.py`
  - `CNF.to_CNF()` again converts through the composite-predicate map by calling `to_NNF(expr, get_composite_predicates())`, restoring the previous CNF representation behavior.

- `sympy/assumptions/ask_generated.py`
  - Reverted the generated known-facts clause set to match the restored facts/CNF behavior.
  - `get_all_known_number_facts()` now contains 47 clauses instead of 81.
  - The newly introduced `even/odd/integer` relationship clause is no longer present.

Test files were not modified.

## pico's patch

```diff
diff --git a/sympy/assumptions/ask_generated.py b/sympy/assumptions/ask_generated.py
index 4ce7579af9..d90cdffc1e 100644
--- a/sympy/assumptions/ask_generated.py
+++ b/sympy/assumptions/ask_generated.py
@@ -13,21 +13,20 @@ def get_all_known_facts():
     Known facts between unary predicates as CNF clauses.
     """
     return {
-        frozenset((Literal(Q.algebraic, False), Literal(Q.complex, True), Literal(Q.transcendental, False))),
+        frozenset((Literal(Q.algebraic, False), Literal(Q.imaginary, True), Literal(Q.transcendental, False))),
+        frozenset((Literal(Q.algebraic, False), Literal(Q.negative, True), Literal(Q.transcendental, False))),
+        frozenset((Literal(Q.algebraic, False), Literal(Q.positive, True), Literal(Q.transcendental, False))),
         frozenset((Literal(Q.algebraic, False), Literal(Q.rational, True))),
-        frozenset((Literal(Q.algebraic, True), Literal(Q.complex, False))),
+        frozenset((Literal(Q.algebraic, False), Literal(Q.transcendental, False), Literal(Q.zero, True))),
+        frozenset((Literal(Q.algebraic, True), Literal(Q.finite, False))),
         frozenset((Literal(Q.algebraic, True), Literal(Q.transcendental, True))),
         frozenset((Literal(Q.antihermitian, False), Literal(Q.hermitian, False), Literal(Q.zero, True))),
         frozenset((Literal(Q.antihermitian, False), Literal(Q.imaginary, True))),
         frozenset((Literal(Q.commutative, False), Literal(Q.finite, True))),
         frozenset((Literal(Q.commutative, False), Literal(Q.infinite, True))),
-        frozenset((Literal(Q.complex, False), Literal(Q.imaginary, True))),
-        frozenset((Literal(Q.complex, False), Literal(Q.real, True))),
-        frozenset((Literal(Q.complex, False), Literal(Q.transcendental, True))),
-        frozenset((Literal(Q.complex, True), Literal(Q.finite, False))),
         frozenset((Literal(Q.complex_elements, False), Literal(Q.real_elements, True))),
         frozenset((Literal(Q.composite, False), Literal(Q.even, True), Literal(Q.positive, True), Literal(Q.prime, False))),
-        frozenset((Literal(Q.composite, True), Literal(Q.integer, False))),
+        frozenset((Literal(Q.composite, True), Literal(Q.even, False), Literal(Q.odd, False))),
         frozenset((Literal(Q.composite, True), Literal(Q.positive, False))),
         frozenset((Literal(Q.composite, True), Literal(Q.prime, True))),
         frozenset((Literal(Q.diagonal, False), Literal(Q.lower_triangular, True), Literal(Q.upper_triangular, True))),
@@ -35,86 +34,53 @@ def get_all_known_facts():
         frozenset((Literal(Q.diagonal, True), Literal(Q.normal, False))),
         frozenset((Literal(Q.diagonal, True), Literal(Q.symmetric, False))),
         frozenset((Literal(Q.diagonal, True), Literal(Q.upper_triangular, False))),
-        frozenset((Literal(Q.even, False), Literal(Q.integer, True), Literal(Q.odd, False))),
+        frozenset((Literal(Q.even, False), Literal(Q.odd, False), Literal(Q.prime, True))),
         frozenset((Literal(Q.even, False), Literal(Q.zero, True))),
-        frozenset((Literal(Q.even, True), Literal(Q.integer, False))),
         frozenset((Literal(Q.even, True), Literal(Q.odd, True))),
-        frozenset((Literal(Q.extended_negative, False), Literal(Q.negative, True))),
-        frozenset((Literal(Q.extended_negative, False), Literal(Q.negative_infinite, True))),
-        frozenset((Literal(Q.extended_negative, True), Literal(Q.negative, False), Literal(Q.negative_infinite, False))),
-        frozenset((Literal(Q.extended_nonnegative, False), Literal(Q.positive, True))),
-        frozenset((Literal(Q.extended_nonnegative, False), Literal(Q.positive_infinite, True))),
-        frozenset((Literal(Q.extended_nonnegative, False), Literal(Q.zero, True))),
-        frozenset((Literal(Q.extended_nonnegative, True), Literal(Q.positive, False), Literal(Q.positive_infinite, False), Literal(Q.zero, False))),
-        frozenset((Literal(Q.extended_nonpositive, False), Literal(Q.negative, True))),
-        frozenset((Literal(Q.extended_nonpositive, False), Literal(Q.negative_infinite, True))),
-        frozenset((Literal(Q.extended_nonpositive, False), Literal(Q.zero, True))),
-        frozenset((Literal(Q.extended_nonpositive, True), Literal(Q.negative, False), Literal(Q.negative_infinite, False), Literal(Q.zero, False))),
-        frozenset((Literal(Q.extended_nonzero, False), Literal(Q.negative, True))),
-        frozenset((Literal(Q.extended_nonzero, False), Literal(Q.negative_infinite, True))),
-        frozenset((Literal(Q.extended_nonzero, False), Literal(Q.positive, True))),
-        frozenset((Literal(Q.extended_nonzero, False), Literal(Q.positive_infinite, True))),
-        frozenset((Literal(Q.extended_nonzero, True), Literal(Q.negative, False), Literal(Q.negative_infinite, False), Literal(Q.positive, False), Literal(Q.positive_infinite, False))),
-        frozenset((Literal(Q.extended_positive, False), Literal(Q.positive, True))),
-        frozenset((Literal(Q.extended_positive, False), Literal(Q.positive_infinite, True))),
-        frozenset((Literal(Q.extended_positive, True), Literal(Q.positive, False), Literal(Q.positive_infinite, False))),
-        frozenset((Literal(Q.extended_real, False), Literal(Q.negative, True))),
-        frozenset((Literal(Q.extended_real, False), Literal(Q.negative_infinite, True))),
-        frozenset((Literal(Q.extended_real, False), Literal(Q.positive, True))),
-        frozenset((Literal(Q.extended_real, False), Literal(Q.positive_infinite, True))),
-        frozenset((Literal(Q.extended_real, False), Literal(Q.zero, True))),
-        frozenset((Literal(Q.extended_real, True), Literal(Q.negative, False), Literal(Q.negative_infinite, False), Literal(Q.positive, False), Literal(Q.positive_infinite, False), Literal(Q.zero, False))),
+        frozenset((Literal(Q.even, True), Literal(Q.rational, False))),
+        frozenset((Literal(Q.finite, False), Literal(Q.transcendental, True))),
         frozenset((Literal(Q.finite, True), Literal(Q.infinite, True))),
         frozenset((Literal(Q.fullrank, False), Literal(Q.invertible, True))),
         frozenset((Literal(Q.fullrank, True), Literal(Q.invertible, False), Literal(Q.square, True))),
-        frozenset((Literal(Q.hermitian, False), Literal(Q.real, True))),
-        frozenset((Literal(Q.imaginary, True), Literal(Q.real, True))),
+        frozenset((Literal(Q.hermitian, False), Literal(Q.negative, True))),
+        frozenset((Literal(Q.hermitian, False), Literal(Q.positive, True))),
+        frozenset((Literal(Q.hermitian, False), Literal(Q.zero, True))),
+        frozenset((Literal(Q.imaginary, True), Literal(Q.negative, True))),
+        frozenset((Literal(Q.imaginary, True), Literal(Q.positive, True))),
+        frozenset((Literal(Q.imaginary, True), Literal(Q.zero, True))),
         frozenset((Literal(Q.infinite, False), Literal(Q.negative_infinite, True))),
         frozenset((Literal(Q.infinite, False), Literal(Q.positive_infinite, True))),
-        frozenset((Literal(Q.integer, False), Literal(Q.odd, True))),
-        frozenset((Literal(Q.integer, False), Literal(Q.prime, True))),
-        frozenset((Literal(Q.integer, True), Literal(Q.rational, False))),
         frozenset((Literal(Q.integer_elements, True), Literal(Q.real_elements, False))),
         frozenset((Literal(Q.invertible, False), Literal(Q.positive_definite, True))),
         frozenset((Literal(Q.invertible, False), Literal(Q.singular, False))),
         frozenset((Literal(Q.invertible, False), Literal(Q.unitary, True))),
         frozenset((Literal(Q.invertible, True), Literal(Q.singular, True))),
         frozenset((Literal(Q.invertible, True), Literal(Q.square, False))),
-        frozenset((Literal(Q.irrational, False), Literal(Q.rational, False), Literal(Q.real, True))),
+        frozenset((Literal(Q.irrational, False), Literal(Q.negative, True), Literal(Q.rational, False))),
+        frozenset((Literal(Q.irrational, False), Literal(Q.positive, True), Literal(Q.rational, False))),
+        frozenset((Literal(Q.irrational, False), Literal(Q.rational, False), Literal(Q.zero, True))),
+        frozenset((Literal(Q.irrational, True), Literal(Q.negative, False), Literal(Q.positive, False), Literal(Q.zero, False))),
         frozenset((Literal(Q.irrational, True), Literal(Q.rational, True))),
-        frozenset((Literal(Q.irrational, True), Literal(Q.real, False))),
         frozenset((Literal(Q.lower_triangular, False), Literal(Q.triangular, True), Literal(Q.upper_triangular, False))),
         frozenset((Literal(Q.lower_triangular, True), Literal(Q.triangular, False))),
-        frozenset((Literal(Q.negative, False), Literal(Q.nonpositive, True), Literal(Q.zero, False))),
-        frozenset((Literal(Q.negative, False), Literal(Q.nonzero, True), Literal(Q.positive, False))),
-        frozenset((Literal(Q.negative, False), Literal(Q.positive, False), Literal(Q.real, True), Literal(Q.zero, False))),
+        frozenset((Literal(Q.negative, False), Literal(Q.positive, False), Literal(Q.rational, True), Literal(Q.zero, False))),
         frozenset((Literal(Q.negative, True), Literal(Q.negative_infinite, True))),
-        frozenset((Literal(Q.negative, True), Literal(Q.nonpositive, False))),
-        frozenset((Literal(Q.negative, True), Literal(Q.nonzero, False))),
         frozenset((Literal(Q.negative, True), Literal(Q.positive, True))),
         frozenset((Literal(Q.negative, True), Literal(Q.positive_infinite, True))),
-        frozenset((Literal(Q.negative, True), Literal(Q.real, False))),
         frozenset((Literal(Q.negative, True), Literal(Q.zero, True))),
         frozenset((Literal(Q.negative_infinite, True), Literal(Q.positive, True))),
         frozenset((Literal(Q.negative_infinite, True), Literal(Q.positive_infinite, True))),
         frozenset((Literal(Q.negative_infinite, True), Literal(Q.zero, True))),
-        frozenset((Literal(Q.nonnegative, False), Literal(Q.positive, True))),
-        frozenset((Literal(Q.nonnegative, False), Literal(Q.zero, True))),
-        frozenset((Literal(Q.nonnegative, True), Literal(Q.positive, False), Literal(Q.zero, False))),
-        frozenset((Literal(Q.nonpositive, False), Literal(Q.zero, True))),
-        frozenset((Literal(Q.nonzero, False), Literal(Q.positive, True))),
         frozenset((Literal(Q.normal, False), Literal(Q.unitary, True))),
         frozenset((Literal(Q.normal, True), Literal(Q.square, False))),
+        frozenset((Literal(Q.odd, True), Literal(Q.rational, False))),
         frozenset((Literal(Q.orthogonal, False), Literal(Q.real_elements, True), Literal(Q.unitary, True))),
         frozenset((Literal(Q.orthogonal, True), Literal(Q.positive_definite, False))),
         frozenset((Literal(Q.orthogonal, True), Literal(Q.unitary, False))),
         frozenset((Literal(Q.positive, False), Literal(Q.prime, True))),
         frozenset((Literal(Q.positive, True), Literal(Q.positive_infinite, True))),
-        frozenset((Literal(Q.positive, True), Literal(Q.real, False))),
         frozenset((Literal(Q.positive, True), Literal(Q.zero, True))),
         frozenset((Literal(Q.positive_infinite, True), Literal(Q.zero, True))),
-        frozenset((Literal(Q.rational, True), Literal(Q.real, False))),
-        frozenset((Literal(Q.real, False), Literal(Q.zero, True))),
         frozenset((Literal(Q.square, False), Literal(Q.symmetric, True))),
         frozenset((Literal(Q.triangular, False), Literal(Q.unit_triangular, True))),
         frozenset((Literal(Q.triangular, False), Literal(Q.upper_triangular, True)))
@@ -158,87 +124,53 @@ def get_all_known_number_facts():
     Known facts between unary predicates for numbers as CNF clauses.
     """
     return {
-        frozenset((Literal(Q.algebraic, False), Literal(Q.complex, True), Literal(Q.transcendental, False))),
+        frozenset((Literal(Q.algebraic, False), Literal(Q.imaginary, True), Literal(Q.transcendental, False))),
+        frozenset((Literal(Q.algebraic, False), Literal(Q.negative, True), Literal(Q.transcendental, False))),
+        frozenset((Literal(Q.algebraic, False), Literal(Q.positive, True), Literal(Q.transcendental, False))),
         frozenset((Literal(Q.algebraic, False), Literal(Q.rational, True))),
-        frozenset((Literal(Q.algebraic, True), Literal(Q.complex, False))),
+        frozenset((Literal(Q.algebraic, False), Literal(Q.transcendental, False), Literal(Q.zero, True))),
+        frozenset((Literal(Q.algebraic, True), Literal(Q.finite, False))),
         frozenset((Literal(Q.algebraic, True), Literal(Q.transcendental, True))),
         frozenset((Literal(Q.antihermitian, False), Literal(Q.hermitian, False), Literal(Q.zero, True))),
         frozenset((Literal(Q.antihermitian, False), Literal(Q.imaginary, True))),
         frozenset((Literal(Q.commutative, False), Literal(Q.finite, True))),
         frozenset((Literal(Q.commutative, False), Literal(Q.infinite, True))),
-        frozenset((Literal(Q.complex, False), Literal(Q.imaginary, True))),
-        frozenset((Literal(Q.complex, False), Literal(Q.real, True))),
-        frozenset((Literal(Q.complex, False), Literal(Q.transcendental, True))),
-        frozenset((Literal(Q.complex, True), Literal(Q.finite, False))),
         frozenset((Literal(Q.composite, False), Literal(Q.even, True), Literal(Q.positive, True), Literal(Q.prime, False))),
-        frozenset((Literal(Q.composite, True), Literal(Q.integer, False))),
+        frozenset((Literal(Q.composite, True), Literal(Q.even, False), Literal(Q.odd, False))),
         frozenset((Literal(Q.composite, True), Literal(Q.positive, False))),
         frozenset((Literal(Q.composite, True), Literal(Q.prime, True))),
-        frozenset((Literal(Q.even, False), Literal(Q.integer, True), Literal(Q.odd, False))),
+        frozenset((Literal(Q.even, False), Literal(Q.odd, False), Literal(Q.prime, True))),
         frozenset((Literal(Q.even, False), Literal(Q.zero, True))),
-        frozenset((Literal(Q.even, True), Literal(Q.integer, False))),
         frozenset((Literal(Q.even, True), Literal(Q.odd, True))),
-        frozenset((Literal(Q.extended_negative, False), Literal(Q.negative, True))),
-        frozenset((Literal(Q.extended_negative, False), Literal(Q.negative_infinite, True))),
-        frozenset((Literal(Q.extended_negative, True), Literal(Q.negative, False), Literal(Q.negative_infinite, False))),
-        frozenset((Literal(Q.extended_nonnegative, False), Literal(Q.positive, True))),
-        frozenset((Literal(Q.extended_nonnegative, False), Literal(Q.positive_infinite, True))),
-        frozenset((Literal(Q.extended_nonnegative, False), Literal(Q.zero, True))),
-        frozenset((Literal(Q.extended_nonnegative, True), Literal(Q.positive, False), Literal(Q.positive_infinite, False), Literal(Q.zero, False))),
-        frozenset((Literal(Q.extended_nonpositive, False), Literal(Q.negative, True))),
-        frozenset((Literal(Q.extended_nonpositive, False), Literal(Q.negative_infinite, True))),
-        frozenset((Literal(Q.extended_nonpositive, False), Literal(Q.zero, True))),
-        frozenset((Literal(Q.extended_nonpositive, True), Literal(Q.negative, False), Literal(Q.negative_infinite, False), Literal(Q.zero, False))),
-        frozenset((Literal(Q.extended_nonzero, False), Literal(Q.negative, True))),
-        frozenset((Literal(Q.extended_nonzero, False), Literal(Q.negative_infinite, True))),
-        frozenset((Literal(Q.extended_nonzero, False), Literal(Q.positive, True))),
-        frozenset((Literal(Q.extended_nonzero, False), Literal(Q.positive_infinite, True))),
-        frozenset((Literal(Q.extended_nonzero, True), Literal(Q.negative, False), Literal(Q.negative_infinite, False), Literal(Q.positive, False), Literal(Q.positive_infinite, False))),
-        frozenset((Literal(Q.extended_positive, False), Literal(Q.positive, True))),
-        frozenset((Literal(Q.extended_positive, False), Literal(Q.positive_infinite, True))),
-        frozenset((Literal(Q.extended_positive, True), Literal(Q.positive, False), Literal(Q.positive_infinite, False))),
-        frozenset((Literal(Q.extended_real, False), Literal(Q.negative, True))),
-        frozenset((Literal(Q.extended_real, False), Literal(Q.negative_infinite, True))),
-        frozenset((Literal(Q.extended_real, False), Literal(Q.positive, True))),
-        frozenset((Literal(Q.extended_real, False), Literal(Q.positive_infinite, True))),
-        frozenset((Literal(Q.extended_real, False), Literal(Q.zero, True))),
-        frozenset((Literal(Q.extended_real, True), Literal(Q.negative, False), Literal(Q.negative_infinite, False), Literal(Q.positive, False), Literal(Q.positive_infinite, False), Literal(Q.zero, False))),
+        frozenset((Literal(Q.even, True), Literal(Q.rational, False))),
+        frozenset((Literal(Q.finite, False), Literal(Q.transcendental, True))),
         frozenset((Literal(Q.finite, True), Literal(Q.infinite, True))),
-        frozenset((Literal(Q.hermitian, False), Literal(Q.real, True))),
-        frozenset((Literal(Q.imaginary, True), Literal(Q.real, True))),
+        frozenset((Literal(Q.hermitian, False), Literal(Q.negative, True))),
+        frozenset((Literal(Q.hermitian, False), Literal(Q.positive, True))),
+        frozenset((Literal(Q.hermitian, False), Literal(Q.zero, True))),
+        frozenset((Literal(Q.imaginary, True), Literal(Q.negative, True))),
+        frozenset((Literal(Q.imaginary, True), Literal(Q.positive, True))),
+        frozenset((Literal(Q.imaginary, True), Literal(Q.zero, True))),
         frozenset((Literal(Q.infinite, False), Literal(Q.negative_infinite, True))),
         frozenset((Literal(Q.infinite, False), Literal(Q.positive_infinite, True))),
-        frozenset((Literal(Q.integer, False), Literal(Q.odd, True))),
-        frozenset((Literal(Q.integer, False), Literal(Q.prime, True))),
-        frozenset((Literal(Q.integer, True), Literal(Q.rational, False))),
-        frozenset((Literal(Q.irrational, False), Literal(Q.rational, False), Literal(Q.real, True))),
+        frozenset((Literal(Q.irrational, False), Literal(Q.negative, True), Literal(Q.rational, False))),
+        frozenset((Literal(Q.irrational, False), Literal(Q.positive, True), Literal(Q.rational, False))),
+        frozenset((Literal(Q.irrational, False), Literal(Q.rational, False), Literal(Q.zero, True))),
+        frozenset((Literal(Q.irrational, True), Literal(Q.negative, False), Literal(Q.positive, False), Literal(Q.zero, False))),
         frozenset((Literal(Q.irrational, True), Literal(Q.rational, True))),
-        frozenset((Literal(Q.irrational, True), Literal(Q.real, False))),
-        frozenset((Literal(Q.negative, False), Literal(Q.nonpositive, True), Literal(Q.zero, False))),
-        frozenset((Literal(Q.negative, False), Literal(Q.nonzero, True), Literal(Q.positive, False))),
-        frozenset((Literal(Q.negative, False), Literal(Q.positive, False), Literal(Q.real, True), Literal(Q.zero, False))),
+        frozenset((Literal(Q.negative, False), Literal(Q.positive, False), Literal(Q.rational, True), Literal(Q.zero, False))),
         frozenset((Literal(Q.negative, True), Literal(Q.negative_infinite, True))),
-        frozenset((Literal(Q.negative, True), Literal(Q.nonpositive, False))),
-        frozenset((Literal(Q.negative, True), Literal(Q.nonzero, False))),
         frozenset((Literal(Q.negative, True), Literal(Q.positive, True))),
         frozenset((Literal(Q.negative, True), Literal(Q.positive_infinite, True))),
-        frozenset((Literal(Q.negative, True), Literal(Q.real, False))),
         frozenset((Literal(Q.negative, True), Literal(Q.zero, True))),
         frozenset((Literal(Q.negative_infinite, True), Literal(Q.positive, True))),
         frozenset((Literal(Q.negative_infinite, True), Literal(Q.positive_infinite, True))),
         frozenset((Literal(Q.negative_infinite, True), Literal(Q.zero, True))),
-        frozenset((Literal(Q.nonnegative, False), Literal(Q.positive, True))),
-        frozenset((Literal(Q.nonnegative, False), Literal(Q.zero, True))),
-        frozenset((Literal(Q.nonnegative, True), Literal(Q.positive, False), Literal(Q.zero, False))),
-        frozenset((Literal(Q.nonpositive, False), Literal(Q.zero, True))),
-        frozenset((Literal(Q.nonzero, False), Literal(Q.positive, True))),
+        frozenset((Literal(Q.odd, True), Literal(Q.rational, False))),
         frozenset((Literal(Q.positive, False), Literal(Q.prime, True))),
         frozenset((Literal(Q.positive, True), Literal(Q.positive_infinite, True))),
-        frozenset((Literal(Q.positive, True), Literal(Q.real, False))),
         frozenset((Literal(Q.positive, True), Literal(Q.zero, True))),
-        frozenset((Literal(Q.positive_infinite, True), Literal(Q.zero, True))),
-        frozenset((Literal(Q.rational, True), Literal(Q.real, False))),
-        frozenset((Literal(Q.real, False), Literal(Q.zero, True)))
+        frozenset((Literal(Q.positive_infinite, True), Literal(Q.zero, True)))
     }
 
 @cacheit
diff --git a/sympy/assumptions/cnf.py b/sympy/assumptions/cnf.py
index cd1d5d87aa..765e18ef6b 100644
--- a/sympy/assumptions/cnf.py
+++ b/sympy/assumptions/cnf.py
@@ -282,7 +282,9 @@ class CNF:
     >>> from sympy.abc import x
     >>> cnf = CNF.from_prop(Q.real(x) & ~Q.zero(x))
     >>> cnf.clauses
-    {frozenset({Literal(Q.real(x), False)}), frozenset({Literal(Q.zero(x), True)})}
+    {frozenset({Literal(Q.zero(x), True)}),
+    frozenset({Literal(Q.negative(x), False),
+    Literal(Q.positive(x), False), Literal(Q.zero(x), False)})}
     """
     def __init__(self, clauses=None):
         if not clauses:
@@ -373,7 +375,8 @@ def all_and(cls, *cnfs):
 
     @classmethod
     def to_CNF(cls, expr):
-        expr = to_NNF(expr)
+        from sympy.assumptions.facts import get_composite_predicates
+        expr = to_NNF(expr, get_composite_predicates())
         expr = distribute_AND_over_OR(expr)
         return expr
 
diff --git a/sympy/assumptions/facts.py b/sympy/assumptions/facts.py
index 4bffc58ab9..d75d895275 100644
--- a/sympy/assumptions/facts.py
+++ b/sympy/assumptions/facts.py
@@ -16,6 +16,26 @@
 from sympy.logic.inference import satisfiable
 
 
+@cacheit
+def get_composite_predicates():
+    # To reduce the complexity of sat solver, these predicates are
+    # transformed into the combination of primitive predicates.
+    return {
+        Q.real : Q.negative | Q.zero | Q.positive,
+        Q.integer : Q.even | Q.odd,
+        Q.nonpositive : Q.negative | Q.zero,
+        Q.nonzero : Q.negative | Q.positive,
+        Q.nonnegative : Q.zero | Q.positive,
+        Q.extended_real : Q.negative_infinite | Q.negative | Q.zero | Q.positive | Q.positive_infinite,
+        Q.extended_positive: Q.positive | Q.positive_infinite,
+        Q.extended_negative: Q.negative | Q.negative_infinite,
+        Q.extended_nonzero: Q.negative_infinite | Q.negative | Q.positive | Q.positive_infinite,
+        Q.extended_nonpositive: Q.negative_infinite | Q.negative | Q.zero,
+        Q.extended_nonnegative: Q.zero | Q.positive | Q.positive_infinite,
+        Q.complex : Q.algebraic | Q.transcendental
+    }
+
+
 @cacheit
 def get_known_facts(x=None):
     """
@@ -64,22 +84,6 @@ def get_number_facts(x = None):
         x = Symbol('x')
 
     fact = And(
-
-        # Composite predicates
-        Equivalent(Q.real(x), Q.negative(x) | Q.zero(x) | Q.positive(x)),
-        Equivalent(Q.integer(x), Q.even(x) | Q.odd(x)),
-        Equivalent(Q.nonpositive(x), Q.negative(x) | Q.zero(x)),
-        Equivalent(Q.nonzero(x), Q.negative(x) | Q.positive(x)),
-        Equivalent(Q.nonnegative(x), Q.zero(x) | Q.positive(x)),
-        Equivalent(Q.extended_real(x),
-                   Q.negative_infinite(x) | Q.negative(x) | Q.zero(x) | Q.positive(x) | Q.positive_infinite(x)),
-        Equivalent(Q.extended_positive(x), Q.positive(x) | Q.positive_infinite(x)),
-        Equivalent(Q.extended_negative(x), Q.negative(x) | Q.negative_infinite(x)),
-        Equivalent(Q.extended_nonzero(x), Q.negative_infinite(x) | Q.negative(x) | Q.positive(x) | Q.positive_infinite(x)),
-        Equivalent(Q.extended_nonpositive(x), Q.negative_infinite(x) | Q.negative(x) | Q.zero(x)),
-        Equivalent(Q.extended_nonnegative(x), Q.zero(x) | Q.positive(x) | Q.positive_infinite(x)),
-        Equivalent(Q.complex(x), Q.algebraic(x) | Q.transcendental(x)),
-
         # primitive predicates for extended real exclude each other.
         Exclusive(Q.negative_infinite(x), Q.negative(x), Q.zero(x),
             Q.positive(x), Q.positive_infinite(x)),

```

## human fix (merged PR #None)

```diff

```

## maintainers' ruling

[oscarbenjamin 2026-03-09] Are you an AI agent? 

[wenwen-666 2026-03-09] No, I'm not an AI agent. I'm a PhD student at Beihang University, and I've developed a tool specifically designed to detect regressions introduced by merged pull requests in SymPy.

 When testing PR #27492 (which aimed to fix exponential query time growth), my tool identified significant regressions: a 72% increase in clause count in known number facts, a 23% rise in arguments of logical expressions, changes in CNF output structure, and new unintended logical relationships in the knowledge base. I documented these findings with detailed test cases to assist with addressing the issues before the PR is fully merged.

 Thank you for your attention to this matter.





------------------&nbsp;原始邮件&nbsp;------------------
发件人:                                                                                                                        "sympy/sympy"                                                                                    ***@***.***&gt;;
发送时间:&nbsp;2026年3月9日(星期一) 晚上7:00
***@***.***&gt;;
***@***.******@***.***&gt;;
主题:&nbsp;Re: [sympy/sympy] Regression: Exponential query time fix causes clause count explosion in known facts (Issue #29358)



oscarbenjamin left a comment (sympy/sympy#29358)
 
Are you an AI agent?
 
—
Reply to this email directly, view it on GitHub, or unsubscribe.
You are receiving this because you authored the thread.Message ID: ***@***.***&gt;

[oscarbenjamin 2026-03-09] If the tool is some kind of generative AI tool then you should make it clearer when commenting on GitHub which parts of what you say are words from yourself and which are the output of the tool.

[TiloRC 2026-03-09] The original issue that https://github.com/sympy/sympy/pull/27492 fixed was about multi variable expressions yet none of the tests you have seem to be multivariable. It doesn't seem like you actually even tried to understand the pull request and associated issue.

Please do not waste other people's time with AI slop. 

[TiloRC 2026-03-10] It seems like you're also opening similar slop prs in other open source projects: https://github.com/pylint-dev/pylint/issues/10909


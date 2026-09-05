# pylint-11175 — https://github.com/pylint-dev/pylint/issues/11175

## reference

F2P: ['tests/test_functional.py::test_functional[comparison_with_callable]']

pico's F2P results: {'tests/test_functional.py::test_functional[comparison_with_callable]': 'FAILED'}

## pico's final report

Implemented the fix in `pylint/checkers/base/comparison_checker.py`.

What changed:
- `_check_callable_comparison` now unwraps `astroid.BoundMethod` proxies before inspecting the underlying callable.
- If the underlying callable is a `nodes.Lambda` (e.g. a lambda assigned as a class attribute and accessed via an instance), it is treated as a bare callable without trying to access `decoratornames()` or iterating over a non-list `.body`, both of which previously caused an `AttributeError`/`TypeError`.
- Normal `FunctionDef` handling (typing `_SpecialForm` checks and ignoring functions that contain `Raise`) is preserved.

Verified:
- The reported reproducer no longer crashes and correctly emits `comparison-with-callable`.
- Existing functional tests, including `comparison_with_callable` and `consider_refactoring_into_while_condition`, pass.
- Full functional test suite passes: 885 passed, 17 skipped.

## pico's patch

```diff
diff --git a/pylint/checkers/base/comparison_checker.py b/pylint/checkers/base/comparison_checker.py
index 4867f8098..29bc1aa03 100644
--- a/pylint/checkers/base/comparison_checker.py
+++ b/pylint/checkers/base/comparison_checker.py
@@ -282,8 +282,19 @@ class ComparisonChecker(_BasicChecker):
             inferred = utils.safe_infer(operand)
             # Ignore callables that raise, as well as typing constants
             # implemented as functions (that raise via their decorator)
-            if (
-                isinstance(inferred, bare_callables)
+            if not isinstance(inferred, bare_callables):
+                continue
+            # A BoundMethod can proxy a Lambda as well as a FunctionDef.
+            # Unwrap the proxy so the Lambda-specific checks below can be used.
+            if isinstance(inferred, astroid.BoundMethod):
+                while isinstance(inferred, astroid.UnboundMethod):
+                    inferred = inferred._proxied
+            if isinstance(inferred, nodes.Lambda):
+                # A Lambda cannot contain a Raise statement and cannot be
+                # decorated, so it is always a bare callable here.
+                number_of_bare_callables += 1
+            elif (
+                isinstance(inferred, nodes.FunctionDef)
                 and "typing._SpecialForm" not in inferred.decoratornames()
                 and not any(isinstance(x, nodes.Raise) for x in inferred.body)
             ):

```

## human fix (merged PR #11186)

```diff
diff --git a/doc/whatsnew/fragments/11175.bugfix b/doc/whatsnew/fragments/11175.bugfix
new file mode 100644
index 00000000000..0b1b05f8e2f
--- /dev/null
+++ b/doc/whatsnew/fragments/11175.bugfix
@@ -0,0 +1,3 @@
+Fixed a crash in ``comparison-with-callable`` when comparing a lambda assigned as a class attribute.
+
+Closes #11175
diff --git a/pylint/checkers/base/comparison_checker.py b/pylint/checkers/base/comparison_checker.py
index 4867f809848..80f97398b34 100644
--- a/pylint/checkers/base/comparison_checker.py
+++ b/pylint/checkers/base/comparison_checker.py
@@ -273,19 +273,28 @@ def _check_callable_comparison(self, node: nodes.Compare) -> None:
         if operator not in COMPARISON_OPERATORS:
             return
 
-        bare_callables = (nodes.FunctionDef, astroid.BoundMethod)
         left_operand, right_operand = node.left, node.ops[0][1]
         # this message should be emitted only when there is comparison of bare callable
         # with non bare callable.
         number_of_bare_callables = 0
         for operand in left_operand, right_operand:
             inferred = utils.safe_infer(operand)
+            # An unbound method on its own is not a bare callable here, but a
+            # bound method proxies the function it was built from, so unwrap it.
+            # This matters because a lambda assigned as a class attribute also
+            # infers to a ``BoundMethod``, and a ``Lambda`` has no
+            # ``decoratornames()`` and its ``body`` is a single expression
+            # instead of a list of statements.
+            while isinstance(inferred, astroid.BoundMethod):
+                inferred = inferred._proxied
+                if isinstance(inferred, astroid.UnboundMethod):
+                    inferred = inferred._proxied
+            if not isinstance(inferred, nodes.FunctionDef):
+                continue
             # Ignore callables that raise, as well as typing constants
             # implemented as functions (that raise via their decorator)
-            if (
-                isinstance(inferred, bare_callables)
-                and "typing._SpecialForm" not in inferred.decoratornames()
-                and not any(isinstance(x, nodes.Raise) for x in inferred.body)
+            if "typing._SpecialForm" not in inferred.decoratornames() and not any(
+                isinstance(x, nodes.Raise) for x in inferred.body
             ):
                 number_of_bare_callables += 1
         if number_of_bare_callables == 1:

```

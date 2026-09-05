# pylint-11025 — https://github.com/pylint-dev/pylint/issues/11025

## reference

F2P: ['tests/test_functional.py::test_functional[regression_11025]']

pico's F2P results: {'tests/test_functional.py::test_functional[regression_11025]': 'PASSED'}

## pico's final report

Implemented a minimal fix in `pylint/checkers/variables.py`.

The crash happened in `_inferred_to_define_name_raise_or_return_for_if_node`:

```python
only_search_else = only_search_else and not val
```

When the inferred condition constant is `NotImplemented`, evaluating `not NotImplemented` performs a boolean-context operation on `NotImplemented`, which raises `TypeError` on Python 3.14 (and a `DeprecationWarning` on earlier versions when warnings are errors).

The surrounding code already avoids this for the `if`-side check by guarding with `val != NotImplemented`. I applied the same guard to the `else`-side check:

```python
only_search_else = only_search_else and (val != NotImplemented and not val)
```

This preserves the existing semantics for every value, including `NotImplemented`, while never putting `NotImplemented` into a boolean context.

Verification performed:
- Reproduced the failure with warnings-as-errors on Python 3.12 (the same code path raises the `TypeError` on Python 3.14).
- Confirmed the reproduction now completes and reports `E0606 possibly-used-before-assignment` without crashing.
- Ran `tests/checkers/unittest_variables.py` (10 passed).
- Ran the `used_before_assignment` functional tests (25 passed, 2 skipped).

## pico's patch

```diff
diff --git a/pylint/checkers/variables.py b/pylint/checkers/variables.py
index 7a982028f..9c1d4cb20 100644
--- a/pylint/checkers/variables.py
+++ b/pylint/checkers/variables.py
@@ -731,7 +731,7 @@ scope_type : {self.scope_type}
                 continue
             val = inferred.value
             only_search_if = only_search_if or (val != NotImplemented and val)
-            only_search_else = only_search_else and not val
+            only_search_else = only_search_else and (val != NotImplemented and not val)
 
         # Only search else branch when test condition is inferred to be false
         if all_inferred and only_search_else:

```

## human fix (merged PR #11026)

```diff
diff --git a/doc/whatsnew/fragments/11025.bugfix b/doc/whatsnew/fragments/11025.bugfix
new file mode 100644
index 00000000000..24e1dafbebe
--- /dev/null
+++ b/doc/whatsnew/fragments/11025.bugfix
@@ -0,0 +1,3 @@
+Fix a crash in the variables checker when ``NotImplemented`` is used as the test of an ``if`` statement, which raised a ``TypeError`` in a boolean context on Python 3.14.
+
+Closes #11025
diff --git a/pylint/checkers/variables.py b/pylint/checkers/variables.py
index 7a982028f69..d94a1f2d34d 100644
--- a/pylint/checkers/variables.py
+++ b/pylint/checkers/variables.py
@@ -730,7 +730,14 @@ def _inferred_to_define_name_raise_or_return_for_if_node(
                 only_search_else = False
                 continue
             val = inferred.value
-            only_search_if = only_search_if or (val != NotImplemented and val)
+            if val is NotImplemented:
+                # ``bool(NotImplemented)`` raises ``TypeError`` on Python 3.14+
+                # (and warned since 3.9). ``NotImplemented`` is the only value
+                # ``Const`` carries whose truthiness is undefined, so treat it
+                # like a non-``Const`` inference: we can't tell which branch runs.
+                only_search_else = False
+                continue
+            only_search_if = only_search_if or bool(val)
             only_search_else = only_search_else and not val
 
         # Only search else branch when test condition is inferred to be false

```

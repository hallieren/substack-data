# pylint-11148 — https://github.com/pylint-dev/pylint/issues/11148

## reference

F2P: ['tests/test_functional.py::test_functional[useless_parent_delegation_py38]']

pico's F2P results: {'tests/test_functional.py::test_functional[useless_parent_delegation_py38]': 'PASSED'}

## pico's final report

Implemented the fix.

## What I changed

In `pylint/checkers/classes/class_checker.py`, the helper `_has_different_parameters_default_value` only iterated over `chain(original.args, original.kwonlyargs)`, skipping `original.posonlyargs`. As a result, a changed default on a positional-only parameter was never detected, causing the false-positive `useless-parent-delegation` (W0246).

The fix adds the positional-only parameters to the iteration:

```python
for param in chain(original.posonlyargs, original.args, original.kwonlyargs):
```

This matches how positional-only arguments are already handled elsewhere in the same checker (e.g. `_signature_from_arguments` uses `chain(arguments.posonlyargs, arguments.args)`).

## Verification

- Reproduced the bug before the fix: a subclass overriding a positional-only param default (`a=1, /` → `a=2, /`) was flagged with W0246, while the regular-argument equivalent was not.
- After the fix:
  - Changed positional-only default → no message.
  - Changed regular positional default → no message (unchanged).
  - Unchanged positional-only default (truly useless delegation) → still flagged.
  - Mixed posonly defaults where only one changes → no message.
- Ran the full functional test suite: `883 passed, 17 skipped`, including the existing `useless_parent_delegation` tests.

Only the source file was modified; no test files or configs were touched, and all scratch files were removed.

## pico's patch

```diff
diff --git a/pylint/checkers/classes/class_checker.py b/pylint/checkers/classes/class_checker.py
index 50d4ebe88..cad4ba1c1 100644
--- a/pylint/checkers/classes/class_checker.py
+++ b/pylint/checkers/classes/class_checker.py
@@ -225,7 +225,7 @@ def _has_different_parameters_default_value(
     if original.args is None or overridden.args is None:
         return False
 
-    for param in chain(original.args, original.kwonlyargs):
+    for param in chain(original.posonlyargs, original.args, original.kwonlyargs):
         try:
             original_default = original.default_value(param.name)
         except astroid.exceptions.NoDefault:

```

## human fix (merged PR #11151)

```diff
diff --git a/doc/whatsnew/fragments/11148.bugfix b/doc/whatsnew/fragments/11148.bugfix
new file mode 100644
index 00000000000..594ca58fd78
--- /dev/null
+++ b/doc/whatsnew/fragments/11148.bugfix
@@ -0,0 +1,4 @@
+Fix a false positive for :ref:`useless-parent-delegation` when an override changes
+the default value of a positional-only parameter.
+
+Closes #11148
diff --git a/pylint/checkers/classes/class_checker.py b/pylint/checkers/classes/class_checker.py
index 50d4ebe8899..cad4ba1c1ca 100644
--- a/pylint/checkers/classes/class_checker.py
+++ b/pylint/checkers/classes/class_checker.py
@@ -225,7 +225,7 @@ def _has_different_parameters_default_value(
     if original.args is None or overridden.args is None:
         return False
 
-    for param in chain(original.args, original.kwonlyargs):
+    for param in chain(original.posonlyargs, original.args, original.kwonlyargs):
         try:
             original_default = original.default_value(param.name)
         except astroid.exceptions.NoDefault:

```

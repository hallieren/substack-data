# pylint-11222 — https://github.com/pylint-dev/pylint/issues/11222

## reference

F2P: ['tests/test_functional.py::test_functional[shallow_copy_environ]']

pico's F2P results: {'tests/test_functional.py::test_functional[shallow_copy_environ]': 'PASSED'}

## pico's final report

## Summary

The crash occurred in `pylint/checkers/utils.py` in `infer_kwarg_from_call`. When a call is made with `**`-unpacked dict literal (e.g. `copy.copy(**{-1: 1})`), the function iterates over the inferred dict items and unconditionally compares each key node's `.value` against the requested keyword name.

Dict keys aren't always constant nodes — here `-1` is parsed as a `UnaryOp` node (no `.value` attribute), causing the `AttributeError: 'UnaryOp' object has no attribute 'value'`.

### Fix

In `pylint/checkers/utils.py`, I guarded the comparison so only `nodes.Const` keys (literal constants) are compared to the keyword name:

```python
for item in inferred.items:
    if isinstance(item[0], nodes.Const) and item[0].value == keyword:
        return item[1]
```

Non-constant/computed keys (such as `UnaryOp`, tuple keys, etc.) are now safely skipped instead of crashing. This matches the fact that only string-literal keys can possibly match a keyword argument name.

### Verification
- Reproduced the original `AttributeError` before the change.
- Confirmed the exact PR example (`copy.copy(**{-1: 1})`) no longer crashes and pylint rates the file normally.
- Confirmed existing behavior is preserved: `copy.copy(**{"x": os.environ})` and `copy.copy(x=os.environ)` still emit `shallow-copy-environ`.
- Ran relevant test suites: `tests/checkers/unittest_utils.py`, `tests/checkers/unittest_stdlib.py`, `tests/checkers/unittest_refactoring.py`, and the `shallow_copy_environ` functional test — all pass.

## pico's patch

```diff
diff --git a/pylint/checkers/utils.py b/pylint/checkers/utils.py
index d1815a1e5..78ee35942 100644
--- a/pylint/checkers/utils.py
+++ b/pylint/checkers/utils.py
@@ -757,7 +757,7 @@ def infer_kwarg_from_call(call_node: nodes.Call, keyword: str) -> nodes.Name | N
         inferred = safe_infer(arg.value)
         if isinstance(inferred, nodes.Dict):
             for item in inferred.items:
-                if item[0].value == keyword:
+                if isinstance(item[0], nodes.Const) and item[0].value == keyword:
                     return item[1]
 
     return None

```

## human fix (merged PR #11225)

```diff
diff --git a/doc/whatsnew/fragments/11222.bugfix b/doc/whatsnew/fragments/11222.bugfix
new file mode 100644
index 0000000000..24fe2d29d3
--- /dev/null
+++ b/doc/whatsnew/fragments/11222.bugfix
@@ -0,0 +1,4 @@
+Fix a crash when a call unpacks a dictionary whose keys are not string
+constants, e.g. ``copy.copy(**{-1: 1})``.
+
+Closes #11222
diff --git a/pylint/checkers/utils.py b/pylint/checkers/utils.py
index d1815a1e5d..543dd7bef1 100644
--- a/pylint/checkers/utils.py
+++ b/pylint/checkers/utils.py
@@ -756,9 +756,11 @@ def infer_kwarg_from_call(call_node: nodes.Call, keyword: str) -> nodes.Name | N
     for arg in call_node.kwargs:
         inferred = safe_infer(arg.value)
         if isinstance(inferred, nodes.Dict):
-            for item in inferred.items:
-                if item[0].value == keyword:
-                    return item[1]
+            for key, value in inferred.items:
+                # Keys can be any expression (or None for '**' unpacking),
+                # only string constants can name a keyword argument.
+                if isinstance(key, nodes.Const) and key.value == keyword:
+                    return value
 
     return None
 

```

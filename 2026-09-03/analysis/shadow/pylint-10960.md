# pylint-10960 — https://github.com/pylint-dev/pylint/issues/10960

## reference

F2P: ['tests/test_functional.py::test_functional[bad_dunder_name]']

pico's F2P results: {'tests/test_functional.py::test_functional[bad_dunder_name]': 'PASSED'}

## pico's final report

Implemented the requested change.

**What changed:**
- Added `__suppress_context__` to `DUNDER_PROPERTIES` in `pylint/constants.py`.

**Why:**
- `pylint/extensions/dunder.py` builds the list of recognized dunder names from `DUNDER_PROPERTIES`, `DUNDER_METHODS`, and `EXTRA_DUNDER_METHODS`.
- `__suppress_context__` is a built-in special attribute on `BaseException` that users may legitimately override, e.g. via a `property` method. Placing it in `DUNDER_PROPERTIES` makes the `bad-dunder-name` checker accept it without affecting the unrelated `unnecessary-dunder-call` checker (which only uses `DUNDER_METHODS`).

**Verification:**
- Reproduced the issue: a method/property named `__suppress_context__` triggered `W3201` before the change.
- After the change, `pylint --load-plugins=pylint.extensions.dunder --enable=bad-dunder-name` reports no warning for it.
- Ran the existing functional test `tests/test_functional.py::test_functional[bad_dunder_name]`, which still passes.

## pico's patch

```diff
diff --git a/pylint/constants.py b/pylint/constants.py
index 6a2481913..b31099baf 100644
--- a/pylint/constants.py
+++ b/pylint/constants.py
@@ -253,6 +253,7 @@ DUNDER_PROPERTIES = [
     "__module__",
     "__sizeof__",
     "__subclasshook__",
+    "__suppress_context__",
     "__weakref__",
 ]
 

```

## human fix (merged PR #10977)

```diff
diff --git a/doc/whatsnew/fragments/10960.false_positive b/doc/whatsnew/fragments/10960.false_positive
new file mode 100644
index 00000000000..3c0874c5c14
--- /dev/null
+++ b/doc/whatsnew/fragments/10960.false_positive
@@ -0,0 +1,3 @@
+Fix a false positive for ``bad-dunder-name`` when there is a user-defined ``__suppress_context__`` attribute on exception subclasses.
+
+Closes #10960
diff --git a/pylint/constants.py b/pylint/constants.py
index 6a2481913b8..b31099baf76 100644
--- a/pylint/constants.py
+++ b/pylint/constants.py
@@ -253,6 +253,7 @@ def _get_pylint_home() -> str:
     "__module__",
     "__sizeof__",
     "__subclasshook__",
+    "__suppress_context__",
     "__weakref__",
 ]
 

```

# pylint-11287 — https://github.com/pylint-dev/pylint/issues/11287

## reference

F2P: ['tests/extensions/test_check_docs_utils.py::test_get_setters_property_with_non_function_attr']

pico's F2P results: {'tests/extensions/test_check_docs_utils.py::test_get_setters_property_with_non_function_attr': 'PASSED'}

## pico's final report

Implemented the fix in `pylint/extensions/_check_docs_utils.py`.

## What changed

In `get_setters_property()`, `class_node.getattr(node.name)` can return class attributes that are not functions, such as an `AssignName` node when a name is assigned before a property setter:

```python
class C:
    prop = None

    @prop.setter
    def prop(self, value):
        raise Exception
```

The code previously passed every returned attribute directly to `utils.decorated_with_property()`, which assumes a `FunctionDef` and accesses `.decorators`, causing the crash.

The fix only calls `decorated_with_property()` when the attribute is actually a `FunctionDef`:

```python
if isinstance(attr, nodes.FunctionDef) and utils.decorated_with_property(attr):
```

## Verification

- Reproduced the crash with the provided example before the fix.
- Confirmed the same command now completes without an `AttributeError`/fatal astroid error.
- Verified normal property setter handling still works.
- Ran the relevant test suites:
  - `tests/extensions/test_check_docs_utils.py` — passed
  - `tests/extensions` — passed
  - Functional docparams tests — passed
  - `tests/checkers/unittest_utils.py` — passed

## pico's patch

```diff
diff --git a/pylint/extensions/_check_docs_utils.py b/pylint/extensions/_check_docs_utils.py
index fd6b52fdc..91e05b21b 100644
--- a/pylint/extensions/_check_docs_utils.py
+++ b/pylint/extensions/_check_docs_utils.py
@@ -63,7 +63,7 @@ def get_setters_property(node: nodes.FunctionDef) -> nodes.FunctionDef | None:
     if property_name and class_node:
         class_attrs: list[nodes.FunctionDef] = class_node.getattr(node.name)
         for attr in class_attrs:
-            if utils.decorated_with_property(attr):
+            if isinstance(attr, nodes.FunctionDef) and utils.decorated_with_property(attr):
                 property_ = attr
                 break
 

```

## human fix (merged PR #11299)

```diff
diff --git a/doc/whatsnew/fragments/11287.bugfix b/doc/whatsnew/fragments/11287.bugfix
new file mode 100644
index 0000000000..4dbbdad7ce
--- /dev/null
+++ b/doc/whatsnew/fragments/11287.bugfix
@@ -0,0 +1,3 @@
+Fix a crash in the ``docparams`` extension (``AttributeError: 'AssignName' object has no attribute 'decorators'``) when a class has non-function attributes sharing the name of a property setter.
+
+Closes #11287
diff --git a/pylint/checkers/utils.py b/pylint/checkers/utils.py
index 9fb1ce0f0a..6ce4688492 100644
--- a/pylint/checkers/utils.py
+++ b/pylint/checkers/utils.py
@@ -804,8 +804,10 @@ def stringify_error(error: str | type[Exception]) -> str:
     return handler.catch(expected_errors)  # type: ignore[no-any-return]
 
 
-def decorated_with_property(node: nodes.FunctionDef) -> bool:
+def decorated_with_property(node: nodes.NodeNG) -> bool:
     """Detect if the given function node is decorated with a property."""
+    if not isinstance(node, nodes.FunctionDef):
+        return False
     if not node.decorators:
         return False
     for decorator in node.decorators.nodes:

```

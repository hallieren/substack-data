# pylint-10823 — https://github.com/pylint-dev/pylint/issues/10823

## reference

F2P: ['tests/test_functional.py::test_functional[undefined_variable_metaclass_nested]']

pico's F2P results: {'tests/test_functional.py::test_functional[undefined_variable_metaclass_nested]': 'PASSED'}

## pico's final report

Implemented the fix in `pylint/checkers/variables.py`.

### What changed

- `_check_metaclasses()` no longer **deletes** metaclass-related names from `NamesConsumer.to_consume`.
  - Deleting made the name invisible to later references, causing the false `undefined-variable`.
  - It now uses `mark_as_consumed()`, which moves the name into `NamesConsumer.consumed` so later uses are still recognized as defined while unused-import/unused-variable checks remain suppressed.

- `_check_classdef_metaclasses()` now records the owning `NamesConsumer` instead of just its `to_consume` dict, allowing the consumption state to be updated properly.

- When deciding whether a metaclass name is defined, it also checks already-consumed names in non-class scopes.
  - This handles cases where the same module/function-level name was used before the class with the metaclass.
  - Consumed class attributes are intentionally not used as a fallback, because class-body names are not visible inside methods.

### Verification

- Reproduced the original issue before the fix.
- Confirmed the reported example no longer emits `E0602`.
- Confirmed additional variants (multiple methods reusing the same metaclass import, prior uses before the metaclass class) also pass.
- Ran the full functional test suite:
  - `869 passed, 17 skipped`
- Ran the variables checker unit tests:
  - `10 passed`

## pico's patch

```diff
diff --git a/pylint/checkers/variables.py b/pylint/checkers/variables.py
index 5add0732c..abc668572 100644
--- a/pylint/checkers/variables.py
+++ b/pylint/checkers/variables.py
@@ -3387,27 +3387,28 @@ class VariablesChecker(BaseChecker):
 
     def _check_metaclasses(self, node: nodes.Module | nodes.FunctionDef) -> None:
         """Update consumption analysis for metaclasses."""
-        consumed: list[tuple[Consumption, str]] = []
+        consumed: list[tuple[NamesConsumer, str]] = []
 
         for child_node in node.get_children():
             if isinstance(child_node, nodes.ClassDef):
                 consumed.extend(self._check_classdef_metaclasses(child_node, node))
 
-        # Pop the consumed items, in order to avoid having
+        # Mark the consumed items as consumed, in order to avoid having
         # unused-import and unused-variable false positives
-        for scope_locals, name in consumed:
-            scope_locals.pop(name, None)
+        for consumer, name in consumed:
+            if name in consumer.to_consume:
+                consumer.mark_as_consumed(name, consumer.to_consume[name])
 
     def _check_classdef_metaclasses(
         self,
         klass: nodes.ClassDef,
         parent_node: nodes.Module | nodes.FunctionDef,
-    ) -> list[tuple[Consumption, str]]:
+    ) -> list[tuple[NamesConsumer, str]]:
         if not klass._metaclass:
             # Skip if this class doesn't use explicitly a metaclass, but inherits it from ancestors
             return []
 
-        consumed: list[tuple[Consumption, str]] = []
+        consumed: list[tuple[NamesConsumer, str]] = []
         metaclass = klass.metaclass()
         name = ""
         match klass._metaclass:
@@ -3428,12 +3429,17 @@ class VariablesChecker(BaseChecker):
         name = METACLASS_NAME_TRANSFORMS.get(name, name)
         if name:
             # check enclosing scopes starting from most local
-            for to_consume in self._to_consume[::-1]:
-                scope_locals = to_consume.to_consume
-                found_nodes = scope_locals.get(name, [])
+            for consumer in self._to_consume[::-1]:
+                found_nodes = consumer.to_consume.get(name, [])
+                if not found_nodes and consumer.scope_type != "class":
+                    # The name may already have been consumed by an earlier use.
+                    # However, consumed class attributes are not visible inside
+                    # methods, so only fall back for other scope types.
+                    found_nodes = consumer.consumed.get(name, [])
                 for found_node in found_nodes:
                     if found_node.lineno <= klass.lineno:
-                        consumed.append((scope_locals, name))
+                        if name in consumer.to_consume:
+                            consumed.append((consumer, name))
                         found = True
                         break
             # Check parent scope

```

## human fix (merged PR #10853)

```diff
diff --git a/doc/whatsnew/fragments/10823.false_positive b/doc/whatsnew/fragments/10823.false_positive
new file mode 100644
index 00000000000..691f9b33e9a
--- /dev/null
+++ b/doc/whatsnew/fragments/10823.false_positive
@@ -0,0 +1,4 @@
+Fix ``undefined-variable`` false positive when a name used as a ``metaclass``
+argument in a nested class is referenced again later in the module.
+
+Closes #10823
diff --git a/pylint/checkers/variables.py b/pylint/checkers/variables.py
index 5add0732c04..fbb7f690720 100644
--- a/pylint/checkers/variables.py
+++ b/pylint/checkers/variables.py
@@ -3387,27 +3387,29 @@ def _check_imports(self, not_consumed: Consumption) -> None:
 
     def _check_metaclasses(self, node: nodes.Module | nodes.FunctionDef) -> None:
         """Update consumption analysis for metaclasses."""
-        consumed: list[tuple[Consumption, str]] = []
+        consumed: list[tuple[NamesConsumer, str, list[nodes.NodeNG]]] = []
 
         for child_node in node.get_children():
             if isinstance(child_node, nodes.ClassDef):
                 consumed.extend(self._check_classdef_metaclasses(child_node, node))
 
-        # Pop the consumed items, in order to avoid having
-        # unused-import and unused-variable false positives
-        for scope_locals, name in consumed:
-            scope_locals.pop(name, None)
+        # Mark the consumed items properly so they move from to_consume
+        # to consumed, avoiding unused-import/unused-variable false positives
+        # while still allowing subsequent references to resolve.
+        for consumer, name, found_nodes in consumed:
+            if name in consumer.to_consume:
+                consumer.mark_as_consumed(name, found_nodes)
 
     def _check_classdef_metaclasses(
         self,
         klass: nodes.ClassDef,
         parent_node: nodes.Module | nodes.FunctionDef,
-    ) -> list[tuple[Consumption, str]]:
+    ) -> list[tuple[NamesConsumer, str, list[nodes.NodeNG]]]:
         if not klass._metaclass:
             # Skip if this class doesn't use explicitly a metaclass, but inherits it from ancestors
             return []
 
-        consumed: list[tuple[Consumption, str]] = []
+        consumed: list[tuple[NamesConsumer, str, list[nodes.NodeNG]]] = []
         metaclass = klass.metaclass()
         name = ""
         match klass._metaclass:
@@ -3433,7 +3435,7 @@ def _check_classdef_metaclasses(
                 found_nodes = scope_locals.get(name, [])
                 for found_node in found_nodes:
                     if found_node.lineno <= klass.lineno:
-                        consumed.append((scope_locals, name))
+                        consumed.append((to_consume, name, found_nodes))
                         found = True
                         break
             # Check parent scope

```

# pylint-11267 — https://github.com/pylint-dev/pylint/issues/11267

## reference

F2P: ['tests/test_functional.py::test_functional[assigning_non_slot]']

pico's F2P results: {'tests/test_functional.py::test_functional[assigning_non_slot]': 'FAILED'}

## pico's final report

The fix is complete. Here is a summary of what I changed and why.

## Problem

In `pylint/checkers/classes/class_checker.py`, the `__class__` assignment checks (`_check_invalid_class_object` and `_check_in_slots` / `_has_same_layout_slots`) assumed that an `AssignAttr.__class__` target's parent is always a plain `Assign` (or a `Tuple` directly inside one) and unconditionally accessed `.parent.value` / `.parent.parent.value`. This crashed for legal-but-unusual targets such as:

- `for foo.__class__ in [...]`
- `with ctx as foo.__class__`
- comprehensions
- bare annotations (`foo.__class__: type`)
- tuple unpacking from a non-literal RHS / nested tuples / short RHS tuples
- unresolvable RHS names in the `__slots__` path (`NameInferenceError`)

## Fix

1. Added a module-level helper `_get_assigned_value(node)` that walks up from an `AssignAttr` target through nested `Tuple`s and returns the exact RHS expression assigned to it, but only when that value can be structurally pinpointed:
   - supports plain `Assign` targets and `AnnAssign` targets with a value (following nested tuple indices into the RHS)
   - returns `None` (unpinpointable) for `for`/`with`/comprehension targets, annotations without a value, unpacking from non-tuple RHS, RHS tuple too short, etc.

2. `_check_invalid_class_object` now uses that helper. If the value can't be pinpointed, it stays quiet instead of crashing.

3. `_check_in_slots` uses the helper for the `__class__` layout check; an unpinpointable value is treated conservatively (stays quiet / no crash), while a pinpointed value still goes through `_has_same_layout_slots`.

4. `_has_same_layout_slots` now catches `astroid.InferenceError` and returns `False`, so `inst.__class__ = UndefinedName` no longer crashes and still emits `assigning-non-slot` (matching the existing behavior for `Uninferable`), and its type hint was widened from `nodes.Name` to `nodes.NodeNG`.

## Verification

- Reproduced the original `F0002` crash before the change, and confirmed all crash cases from the PR report now run without crashing.
- Confirmed expected diagnostics are preserved/emitted correctly: existing `invalid-class-object` tuple/unpacking cases still fire, `assigning-non-slot` is emitted for same-layout/slot mismatches and for unresolvable names, while unpinpointable contexts stay quiet.
- Ran the full functional test suite (`887 passed, 30 skipped`) and `tests/checkers` (`406 passed`), plus the specific `invalid_class_object` / `assigning_non_slot` functional tests.

## pico's patch

```diff
diff --git a/pylint/checkers/classes/class_checker.py b/pylint/checkers/classes/class_checker.py
index b23045907..223379aef 100644
--- a/pylint/checkers/classes/class_checker.py
+++ b/pylint/checkers/classes/class_checker.py
@@ -478,9 +478,12 @@ def _is_attribute_property(name: str, klass: nodes.ClassDef) -> bool:
 
 
 def _has_same_layout_slots(
-    slots: list[nodes.Const | None], assigned_value: nodes.Name
+    slots: list[nodes.Const | None], assigned_value: nodes.NodeNG
 ) -> bool:
-    inferred = next(assigned_value.infer())
+    try:
+        inferred = next(assigned_value.infer())
+    except astroid.InferenceError:
+        return False
     if isinstance(inferred, nodes.ClassDef):
         other_slots = inferred.slots()
         if all(
@@ -491,6 +494,37 @@ def _has_same_layout_slots(
     return False
 
 
+def _get_assigned_value(node: nodes.AssignAttr) -> nodes.NodeNG | None:
+    """Return the expression assigned to an AssignAttr target, if any.
+
+    Returns None when the assigned value cannot be pinpointed from the syntax,
+    for example when the target is a ``for`` loop, ``with`` statement,
+    comprehension or annotation-without-value target, or when unpacking from a
+    RHS that is not a literal tuple.
+    """
+    target: nodes.NodeNG = node
+    indices: list[int] = []
+    while isinstance(target.parent, nodes.Tuple):
+        indices.append(target.parent.elts.index(target))
+        target = target.parent
+    if isinstance(target.parent, nodes.Assign):
+        value = target.parent.value
+    elif isinstance(target.parent, nodes.AnnAssign):
+        value = target.parent.value
+    else:
+        return None
+    if value is None:
+        return None
+    for index in reversed(indices):
+        if not isinstance(value, nodes.Tuple):
+            return None
+        try:
+            value = value.elts[index]
+        except IndexError:
+            return None
+    return value
+
+
 MSGS: dict[str, MessageDefinitionTuple] = {
     "F0202": (
         "Unable to check methods signature (%s / %s)",
@@ -1737,18 +1771,13 @@ a metaclass class method.",
     def _check_invalid_class_object(self, node: nodes.AssignAttr) -> None:
         if not node.attrname == "__class__":
             return
-        if isinstance(node.parent, nodes.Tuple):
-            class_index = -1
-            for i, elt in enumerate(node.parent.elts):
-                if hasattr(elt, "attrname") and elt.attrname == "__class__":
-                    class_index = i
-            if class_index == -1:
-                # This should not happen because we checked that the node name
-                # is '__class__' earlier, but let's not be too confident here
-                return  # pragma: no cover
-            inferred = safe_infer(node.parent.parent.value.elts[class_index])
-        else:
-            inferred = safe_infer(node.parent.value)
+        assigned_value = _get_assigned_value(node)
+        if assigned_value is None:
+            # We cannot determine the assigned value (e.g. target of a for
+            # loop, with statement, comprehension, or an annotation without a
+            # value), so we stay quiet like other uninferable cases.
+            return
+        inferred = safe_infer(assigned_value)
         match inferred:
             case nodes.ClassDef() | util.UninferableBase() | None:
                 # If uninferable, we allow it to prevent false positives
@@ -1824,10 +1853,12 @@ a metaclass class method.",
                     if _has_data_descriptor(klass, node.attrname):
                         # Descriptors circumvent the slots mechanism as well.
                         return
-                if node.attrname == "__class__" and _has_same_layout_slots(
-                    slots, node.parent.value
-                ):
-                    return
+                if node.attrname == "__class__":
+                    assigned_value = _get_assigned_value(node)
+                    if assigned_value is None or _has_same_layout_slots(
+                        slots, assigned_value
+                    ):
+                        return
                 self.add_message(
                     "assigning-non-slot",
                     args=(node.attrname,),

```

## human fix (merged PR #11268)

```diff
diff --git a/doc/whatsnew/fragments/11267.bugfix b/doc/whatsnew/fragments/11267.bugfix
new file mode 100644
index 00000000000..73ca479181b
--- /dev/null
+++ b/doc/whatsnew/fragments/11267.bugfix
@@ -0,0 +1,3 @@
+Fix a crash in :ref:`invalid-class-object` and :ref:`assigning-non-slot` when ``__class__`` is assigned outside a simple assignment (e.g. ``for obj.__class__ in classes:``).
+
+Closes #11267
diff --git a/pylint/checkers/classes/class_checker.py b/pylint/checkers/classes/class_checker.py
index b230459079d..11c840cf34a 100644
--- a/pylint/checkers/classes/class_checker.py
+++ b/pylint/checkers/classes/class_checker.py
@@ -478,11 +478,20 @@ def _is_attribute_property(name: str, klass: nodes.ClassDef) -> bool:
 
 
 def _has_same_layout_slots(
-    slots: list[nodes.Const | None], assigned_value: nodes.Name
+    slots: list[nodes.Const | None], assigned_value: nodes.NodeNG
 ) -> bool:
-    inferred = next(assigned_value.infer())
+    try:
+        inferred = next(assigned_value.infer())
+    except astroid.InferenceError:
+        # An unresolvable value gets the same answer as any other
+        # value that is not a class definition.
+        return False
     if isinstance(inferred, nodes.ClassDef):
         other_slots = inferred.slots()
+        if other_slots is None:
+            # A class without ``__slots__`` anywhere in its mro has a
+            # different layout, which CPython rejects at runtime too.
+            return False
         if all(
             first_slot and second_slot and first_slot.value == second_slot.value
             for (first_slot, second_slot) in zip_longest(slots, other_slots)
@@ -491,6 +500,22 @@ def _has_same_layout_slots(
     return False
 
 
+def _assigned_value(node: nodes.AssignAttr) -> nodes.NodeNG | None:
+    """Return the value bound to ``node``, if a single one can be pinpointed.
+
+    An assignment statement carries the value it binds, and a starred target
+    (``head, *foo.attr = ...``) is resolved by astroid through the target
+    itself. A for-loop, ``with``, or comprehension target has no such value,
+    and neither has a bare annotation (``foo.attr: int``).
+    """
+    parent = node.parent
+    if not isinstance(
+        parent, (nodes.Assign, nodes.AnnAssign, nodes.AugAssign, nodes.Starred)
+    ):
+        return None
+    return parent.value
+
+
 MSGS: dict[str, MessageDefinitionTuple] = {
     "F0202": (
         "Unable to check methods signature (%s / %s)",
@@ -1737,7 +1762,15 @@ def visit_assignattr(self, node: nodes.AssignAttr) -> None:
     def _check_invalid_class_object(self, node: nodes.AssignAttr) -> None:
         if not node.attrname == "__class__":
             return
-        if isinstance(node.parent, nodes.Tuple):
+        if isinstance(node.parent, (nodes.Tuple, nodes.List)):
+            assign_node = node.parent.parent
+            if not isinstance(assign_node, nodes.Assign) or not isinstance(
+                assign_node.value, (nodes.Tuple, nodes.List)
+            ):
+                # A for-loop or ``with`` tuple target, a nested tuple, or an
+                # unpacked call result: the value assigned to ``__class__``
+                # cannot be pinpointed, keep quiet to avoid false positives.
+                return
             class_index = -1
             for i, elt in enumerate(node.parent.elts):
                 if hasattr(elt, "attrname") and elt.attrname == "__class__":
@@ -1746,9 +1779,17 @@ def _check_invalid_class_object(self, node: nodes.AssignAttr) -> None:
                 # This should not happen because we checked that the node name
                 # is '__class__' earlier, but let's not be too confident here
                 return  # pragma: no cover
-            inferred = safe_infer(node.parent.parent.value.elts[class_index])
+            if class_index >= len(assign_node.value.elts):
+                # Unbalanced unpacking, which fails at runtime anyway.
+                return
+            inferred = safe_infer(assign_node.value.elts[class_index])
         else:
-            inferred = safe_infer(node.parent.value)
+            assigned_value = _assigned_value(node)
+            if assigned_value is None:
+                # A for-loop, ``with``, or comprehension target, or a bare
+                # annotation: there is no assigned value to check.
+                return
+            inferred = safe_infer(assigned_value)
         match inferred:
             case nodes.ClassDef() | util.UninferableBase() | None:
                 # If uninferable, we allow it to prevent false positives
@@ -1824,10 +1865,15 @@ def _check_in_slots(self, node: nodes.AssignAttr) -> None:
                     if _has_data_descriptor(klass, node.attrname):
                         # Descriptors circumvent the slots mechanism as well.
                         return
-                if node.attrname == "__class__" and _has_same_layout_slots(
-                    slots, node.parent.value
-                ):
-                    return
+                if node.attrname == "__class__":
+                    # Without a single assigned value there is no slots layout
+                    # to compare against, e.g. for a for-loop, ``with``, or
+                    # tuple-unpacking target.
+                    assigned_value = _assigned_value(node)
+                    if assigned_value is None:
+                        return
+                    if _has_same_layout_slots(slots, assigned_value):
+                        return
                 self.add_message(
                     "assigning-non-slot",
                     args=(node.attrname,),

```

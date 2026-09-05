# pylint-10909-nofix — https://github.com/pylint-dev/pylint/issues/10909

## reference

F2P: []

pico's F2P results: {}

## pico's final report



## pico's patch

```diff
diff --git a/pylint/pyreverse/diagrams.py b/pylint/pyreverse/diagrams.py
index 70ee4a5e1..6c2b2c1ee 100644
--- a/pylint/pyreverse/diagrams.py
+++ b/pylint/pyreverse/diagrams.py
@@ -6,6 +6,7 @@
 
 from __future__ import annotations
 
+from collections import defaultdict
 from collections.abc import Iterable
 from typing import TYPE_CHECKING, Any
 
@@ -18,6 +19,14 @@ from pylint.pyreverse.utils import FilterMixIn, get_annotation_label
 if TYPE_CHECKING:
     from pylint.pyreverse.inspector import Linker
 
+_CLASS_INFO_FIELDS = (
+    "locals_type",
+    "instance_attrs_type",
+    "compositions_type",
+    "aggregations_type",
+    "associations_type",
+)
+
 
 class Figure:
     """Base class for counter handling."""
@@ -85,7 +94,7 @@ class ClassDiagram(Figure, FilterMixIn):
 
     TYPE = "class"
 
-    def __init__(self, title: str, mode: str, linker: Linker) -> None:
+    def __init__(self, title: str, mode: str, linker: Linker | None = None) -> None:
         FilterMixIn.__init__(self, mode)
         Figure.__init__(self)
         self.title = title
@@ -95,6 +104,37 @@ class ClassDiagram(Figure, FilterMixIn):
         self.relationships: dict[str, list[Relationship]] = {}
         self._nodes: dict[nodes.NodeNG, DiagramEntity] = {}
 
+    def _get_class_info(self, node: nodes.ClassDef) -> Any:
+        """Return the analysis info for a class.
+
+        Diagrams created without an explicit linker use the legacy attributes
+        that are still exposed on visited astroid nodes.  When those attributes
+        are present they also back the dataclass info, so using them avoids an
+        extra dictionary lookup.
+        """
+        if all(hasattr(node, attr) for attr in _CLASS_INFO_FIELDS):
+            return node
+        if self.linker is not None:
+            return self.linker.class_info[node]
+        for attr in _CLASS_INFO_FIELDS:
+            if not hasattr(node, attr):
+                setattr(node, attr, defaultdict(list))
+        return node
+
+    def _get_module_info(self, node: nodes.Module) -> Any:
+        """Return the analysis info for a module."""
+        if hasattr(node, "depends") and hasattr(node, "locals_type"):
+            return node
+        if self.linker is not None:
+            return self.linker.module_info[node]
+        if not hasattr(node, "locals_type"):
+            node.locals_type = defaultdict(list)
+        if not hasattr(node, "depends"):
+            node.depends = []
+        if not hasattr(node, "type_depends"):
+            node.type_depends = []
+        return node
+
     def get_relationships(self, role: str) -> Iterable[Relationship]:
         # sorted to get predictable (hence testable) results
         return sorted(
@@ -122,10 +162,13 @@ class ClassDiagram(Figure, FilterMixIn):
                 return rel
         raise KeyError(relation_type)
 
-    def get_attrs(self, node: nodes.ClassDef) -> list[str]:
+    def get_attrs(
+        self, node: nodes.ClassDef, info: Any | None = None
+    ) -> list[str]:
         """Return visible attributes, possibly with class name."""
         attrs = []
-        info = self.linker.class_info[node]
+        if info is None:
+            info = self._get_class_info(node)
 
         # Collect functions decorated with @property
         properties = {
@@ -228,8 +271,8 @@ class ClassDiagram(Figure, FilterMixIn):
         """Extract relationships between nodes in the diagram."""
         for obj in self.classes():
             node = obj.node
-            info = self.linker.class_info[node]
-            obj.attrs = self.get_attrs(node)
+            info = self._get_class_info(node)
+            obj.attrs = self.get_attrs(node, info)
             obj.methods = self.get_methods(node)
             obj.shape = "class"
 
@@ -337,7 +380,7 @@ class PackageDiagram(ClassDiagram):
         """Add dependencies created by from-imports."""
         mod_name = node.root().name
         package = self.module(mod_name).node
-        info = self.linker.module_info[package]
+        info = self._get_module_info(package)
 
         if from_module in info.depends:
             return
@@ -359,7 +402,7 @@ class PackageDiagram(ClassDiagram):
                 continue
         for package_obj in self.modules():
             package_obj.shape = "package"
-            info = self.linker.module_info[package_obj.node]
+            info = self._get_module_info(package_obj.node)
             # dependencies
             for dep_name in info.depends:
                 try:
diff --git a/pylint/pyreverse/inspector.py b/pylint/pyreverse/inspector.py
index 07386ba52..a1d6f2859 100644
--- a/pylint/pyreverse/inspector.py
+++ b/pylint/pyreverse/inspector.py
@@ -12,6 +12,7 @@ from __future__ import annotations
 import os
 import traceback
 from abc import ABC, abstractmethod
+from collections import defaultdict
 from collections.abc import Callable, Sequence
 
 import astroid
@@ -25,6 +26,41 @@ from pylint.checkers.utils import safe_infer
 from pylint.pyreverse import utils
 from pylint.pyreverse.node_info import ClassInfo, FunctionInfo, InfoDict, ModuleInfo
 
+_CLASS_INFO_ATTRS = (
+    "locals_type",
+    "instance_attrs_type",
+    "compositions_type",
+    "aggregations_type",
+    "associations_type",
+)
+
+
+def _ensure_class_info_attrs(node: nodes.ClassDef) -> nodes.ClassDef:
+    """Attach the legacy analysis attributes to ``node`` if needed.
+
+    Before the dataclass refactoring these attributes were stored directly on
+    astroid nodes.  We keep them around (backed by the same dicts used by the
+    info dataclasses) so code written against the old API keeps working.
+    """
+    for attr in _CLASS_INFO_ATTRS:
+        if not hasattr(node, attr):
+            setattr(node, attr, defaultdict(list))
+    return node
+
+
+def _class_info_from_parent(
+    parent: nodes.ClassDef, info: ClassInfo | None
+) -> ClassInfo | nodes.ClassDef:
+    """Return the analysis object to write to.
+
+    New callers pass an explicit ``ClassInfo``; old callers omit it and expect
+    the data to live on the astroid ``ClassDef`` node.
+    """
+    if info is not None:
+        return info
+    return _ensure_class_info_attrs(parent)
+
+
 _WrapperFuncT = Callable[
     [Callable[[str], nodes.Module], str, bool], nodes.Module | None
 ]
@@ -135,18 +171,34 @@ class Linker(IdGeneratorMixIn, utils.LocalsVisitor):
     def visit_module(self, node: nodes.Module) -> None:
         """Visit an nodes.Module node and optionally assign a unique id."""
         info = self.module_info[node]
+        # Compatibility with the pre-dataclass API where analysis data was
+        # stored directly on the astroid nodes.
+        node.locals_type = info.locals_type
+        node.depends = info.depends
+        node.type_depends = info.type_depends
         if self.tag:
             info.uid = self.generate_id()
+            node.uid = info.uid
 
     def visit_classdef(self, node: nodes.ClassDef) -> None:
         """Visit an nodes.Class node and optionally assign a unique id."""
         info = self.class_info[node]
+        # Compatibility with the pre-dataclass API where analysis data was
+        # stored directly on the astroid nodes.
+        node.locals_type = info.locals_type
+        node.instance_attrs_type = info.instance_attrs_type
+        node.compositions_type = info.compositions_type
+        node.aggregations_type = info.aggregations_type
+        node.associations_type = info.associations_type
         if self.tag:
             info.uid = self.generate_id()
+            node.uid = info.uid
         # resolve ancestors
         for baseobj in node.ancestors(recurs=False):
             base_info = self.class_info[baseobj]
             base_info.specializations.append(node)
+            # Compatibility with the pre-dataclass API.
+            baseobj.specializations = base_info.specializations
         # resolve instance attributes
         for assignattrs in tuple(node.instance_attrs.values()):
             for assignattr in assignattrs:
@@ -165,8 +217,12 @@ class Linker(IdGeneratorMixIn, utils.LocalsVisitor):
     def visit_functiondef(self, node: nodes.FunctionDef) -> None:
         """Visit an nodes.Function node and optionally assign a unique id."""
         info = self.function_info[node]
+        # Compatibility with the pre-dataclass API where analysis data was
+        # stored directly on the astroid nodes.
+        node.locals_type = info.locals_type
         if self.tag:
             info.uid = self.generate_id()
+            node.uid = info.uid
 
     def visit_assignname(self, node: nodes.AssignName) -> None:
         """Visit an AssignName node and update locals_type for its frame."""
@@ -194,13 +250,29 @@ class Linker(IdGeneratorMixIn, utils.LocalsVisitor):
         locals_type[node.name] = list(set(current) | utils.infer_node(node))
 
     @staticmethod
-    def handle_assignattr_type(node: nodes.AssignAttr, info: ClassInfo) -> None:
+    def handle_assignattr_type(
+        node: nodes.AssignAttr,
+        parent: nodes.ClassDef | ClassInfo | None = None,
+        *,
+        info: ClassInfo | None = None,
+    ) -> None:
         """Handle an astroid.assignattr node.
 
         handle instance_attrs_type
         """
-        current = set(info.instance_attrs_type[node.attrname])
-        info.instance_attrs_type[node.attrname] = list(current | utils.infer_node(node))
+        parent_or_info = parent if parent is not None else info
+        if parent_or_info is None:
+            raise TypeError("handle_assignattr_type() missing parent/info argument")
+        if isinstance(parent_or_info, nodes.ClassDef):
+            class_info: ClassInfo | nodes.ClassDef = _ensure_class_info_attrs(
+                parent_or_info
+            )
+        else:
+            class_info = parent_or_info
+        current = set(class_info.instance_attrs_type[node.attrname])
+        class_info.instance_attrs_type[node.attrname] = list(
+            current | utils.infer_node(node)
+        )
 
     def visit_import(self, node: nodes.Import) -> None:
         """Visit an nodes.Import node.
@@ -272,7 +344,7 @@ class RelationshipHandlerInterface(ABC):
         self,
         node: nodes.AssignAttr | nodes.AssignName,
         parent: nodes.ClassDef,
-        info: ClassInfo,
+        info: ClassInfo | None = None,
     ) -> None:
         raise NotImplementedError()
 
@@ -289,7 +361,7 @@ class AbstractRelationshipHandler(RelationshipHandlerInterface):
     class.
     """
 
-    _next_handler: RelationshipHandlerInterface
+    _next_handler: RelationshipHandlerInterface | None = None
 
     def set_next(
         self, handler: RelationshipHandlerInterface
@@ -302,9 +374,11 @@ class AbstractRelationshipHandler(RelationshipHandlerInterface):
         self,
         node: nodes.AssignAttr | nodes.AssignName,
         parent: nodes.ClassDef,
-        info: ClassInfo,
+        info: ClassInfo | None = None,
     ) -> None:
-        if self._next_handler:
+        if info is None:
+            info = _ensure_class_info_attrs(parent)
+        if self._next_handler is not None:
             self._next_handler.handle(node, parent, info)
 
 
@@ -315,8 +389,9 @@ class CompositionsHandler(AbstractRelationshipHandler):
         self,
         node: nodes.AssignAttr | nodes.AssignName,
         parent: nodes.ClassDef,
-        info: ClassInfo,
+        info: ClassInfo | None = None,
     ) -> None:
+        info = _class_info_from_parent(parent, info)
         # If the node is not part of an assignment, pass to next handler
         if not isinstance(node.parent, (nodes.AnnAssign, nodes.Assign)):
             super().handle(node, parent, info)
@@ -371,8 +446,9 @@ class AggregationsHandler(AbstractRelationshipHandler):
         self,
         node: nodes.AssignAttr | nodes.AssignName,
         parent: nodes.ClassDef,
-        info: ClassInfo,
+        info: ClassInfo | None = None,
     ) -> None:
+        info = _class_info_from_parent(parent, info)
         # If the node is not part of an assignment, pass to next handler
         if not isinstance(node.parent, (nodes.AnnAssign, nodes.Assign)):
             super().handle(node, parent, info)
@@ -427,8 +503,9 @@ class AssociationsHandler(AbstractRelationshipHandler):
         self,
         node: nodes.AssignAttr | nodes.AssignName,
         parent: nodes.ClassDef,
-        info: ClassInfo,
+        info: ClassInfo | None = None,
     ) -> None:
+        info = _class_info_from_parent(parent, info)
         # Extract the name to handle both AssignAttr and AssignName nodes
         name = node.attrname if isinstance(node, nodes.AssignAttr) else node.name
 

```

## human fix (merged PR #None)

```diff

```

## maintainers' ruling

[DanielNoord 2026-03-09] This is bogus report and clearly AI generated.

The API change is fine, it was discussed and was not considered breaking.

The `ImportError` is honestly ridiculous as you're trying to import something that was introduced in the PR. I'm not even sure what you are testing here.

The performance regression also can't be true since you're using code that in "Test case 1" you show doesn't work.

Please stop filing these reports. They are a waste of our time and I'm very close to blocking you. See also https://github.com/marshmallow-code/marshmallow/issues/2915


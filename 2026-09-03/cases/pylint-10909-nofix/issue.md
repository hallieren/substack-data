# Regression：Refactor pyreverse to use dataclass wrappers introduces API-breaking changes and performance regression （PR 10820:）

### Bug description

```python
PR #10820 refactored pyreverse to use dataclass wrappers (`ClassInfo`, `ModuleInfo`, `FunctionInfo`) instead of modifying astroid nodes directly. However, this change introduces several backward-incompatible API changes and performance regressions that break existing code that relies on pyreverse's public interfaces.

The following test cases demonstrate the regressions:

### Test Case 1: ClassDiagram constructor signature change (API break)


import astroid
from pylint.pyreverse.diagrams import ClassDiagram

# Create a ClassDef node
node = astroid.extract_node('''
class MyClass:
    attr1: int
    attr2: str
''')

# Before PR #10820 - this worked
diagram = ClassDiagram(title='TestDiagram', mode='ALL')
attrs = diagram.get_attrs(node)  # This would work
Before PR #10820 output:
Step 1: Creating mock linker with class_info
linker created: <MockLinker object at 0x...>
Step 2: Creating a ClassDef node
node type: <class 'astroid.nodes.scoped_nodes.scoped_nodes.ClassDef'>
Step 3: Instantiating ClassDiagram
diagram title: TestDiagram
diagram mode: ALL
Step 4: Calling get_attrs
get_attrs executed successfully
After PR #10820 output:
Step 1: Creating mock linker with class_info
linker created: <MockLinker object at 0x...>
Step 2: Creating a ClassDef node
node type: <class 'astroid.nodes.scoped_nodes.scoped_nodes.ClassDef'>
Step 3: Instantiating ClassDiagram
TypeError: ClassDiagram.__init__() missing 1 required positional argument: 'linker'

Test Case 2: Relationship handlers API change

from astroid import nodes
from pylint.pyreverse.inspector import CompositionsHandler, ClassInfo

# Before PR #10820 - this worked
handler = CompositionsHandler()
parent = nodes.ClassDef(name='TestClass')
attr_node = nodes.AssignAttr(attrname='x')
handler.handle(attr_node, parent)  # This worked

Before PR #10820 output:
ImportError: cannot import name 'ClassInfo' from 'pylint.pyreverse.inspector'
After PR #10820 output:
TypeError: ClassDef.__init__() missing 3 required positional arguments: 'lineno', 'col_offset', and 'parent'
Test Case 3: Performance regression
The same operation that took 0.199s before PR #10820 now takes 0.566s (2.9x slowdown) due to additional dictionary lookups:
# Same code as Test Case 1
diagram = ClassDiagram(title='TestDiagram', mode='ALL')
attrs = diagram.get_attrs(node)
Before PR #10820 execution time: 0.199s
After PR #10820 execution time: 0.566s (2.9x slower)
```

### Configuration

```ini
N/A - The issue occurs with default pyreverse usage.
```

### Command used

```shell
python -c "from pylint.pyreverse.diagrams import ClassDiagram; ClassDiagram(title='test', mode='ALL')"
```

### Pylint output

```python
TypeError: ClassDiagram.__init__() missing 1 required positional argument: 'linker'
```

### Expected behavior

The API should remain backward compatible. Changes to internal data structures should not affect public interfaces. Specifically:

ClassDiagram.__init__ should maintain its original signature or provide backward compatibility (e.g., making linker optional with a default)

Relationship handlers should maintain compatible method signatures

Performance should not degrade significantly (2.9x slowdown is unacceptable)

### Pylint version

```shell
Tested on:

Before PR: pylint-dev/pylint@main (pre-#10820)

After PR: pylint-dev/pylint@main (with #10820 merged)
```

### OS / Environment

Linux (Ubuntu 22.04) / Python 3.10

### Additional dependencies

```python
The 7 regression cases identified by our test suite include:

3 cases of API signature changes

3 cases of exception type changes (ImportError → TypeError)

1 case with 2.9x performance degradation

These regressions affect:

Any external code directly instantiating ClassDiagram or PackageDiagram

Any code subclassing or using the relationship handlers

Performance-sensitive applications using pyreverse

The refactoring direction (using dataclasses for analysis data) is good, but it needs to be implemented with backward compatibility in mind. Suggested fixes:

Make linker parameter optional in diagram constructors

Add compatibility properties to astroid nodes that delegate to the new info classes

Optimize the dictionary lookups to reduce performance impact
```

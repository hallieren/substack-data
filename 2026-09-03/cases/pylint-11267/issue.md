# Crash `AttributeError: 'For' object has no attribute 'value'` when `x.__class__` is a for-loop, `with`, or unpacking target

### Bug description

During a code correctness review of the class checker I found that any code where `x.__class__` appears as an assignment target *outside* a plain assignment statement makes the whole module fail with a fatal `astroid-error` (F0002), so every other message for that file is lost.

Minimal reproducer:

```python
class Foo:
    pass


def f(foo):
    for foo.__class__ in [Foo]:
        pass
```

`_check_invalid_class_object` assumes the parent of the `AssignAttr` is a plain assignment with a `.value`, but for a `for` loop target the parent is the `For` node:

```
Exception on node <AssignAttr.__class__ l.6 at 0x...> in file 'crash_for.py'
Traceback (most recent call last):
  File "pylint/utils/ast_walker.py", line 87, in walk
    callback(astroid)
  File "pylint/checkers/classes/class_checker.py", line 1735, in visit_assignattr
    self._check_invalid_class_object(node)
  File "pylint/checkers/classes/class_checker.py", line 1751, in _check_invalid_class_object
    inferred = safe_infer(node.parent.value)
AttributeError: 'For' object has no attribute 'value'
crash_for.py:1:0: F0002: crash_for.py: Fatal error while checking 'crash_for.py'. ... (astroid-error)
```

The same unchecked assumptions crash on the whole family of legal (if unusual) constructs — all reproduced locally on `main` (4be9585) and 4.0.7:

```python
with ctx as foo.__class__: ...            # AttributeError: 'With' object has no attribute 'value'
[0 for foo.__class__ in [Foo]]            # AttributeError: 'Comprehension' object has no attribute 'value'
foo.__class__: type                       # AttributeError: 'NoneType' object has no attribute 'infer'
foo.__class__, x = get_pair()             # AttributeError: 'Call' object has no attribute 'elts'   (line 1749)
for foo.__class__, x in [(Foo, 1)]: ...   # AttributeError: 'For' object has no attribute 'value'   (line 1749)
(a.x, foo.__class__), y = (1, Foo), 2     # AttributeError: 'ClassDef' object has no attribute 'value'
x, foo.__class__ = (Foo,)                 # IndexError: list index out of range
```

The `assigning-non-slot` path has the same problem when the instance's class defines `__slots__`, in `_check_in_slots` (line 1827, `node.parent.value` again) and in `_has_same_layout_slots` (line 483, `next(assigned_value.infer())` without handling `astroid.InferenceError`):

```python
class A:
    __slots__ = ["x"]

class B:
    __slots__ = ["x"]

def f():
    inst = A()
    for inst.__class__ in [B]:       # AttributeError: 'For' object has no attribute 'value' (line 1827)
        pass
    inst.__class__, y = B, 1         # AttributeError: 'ClassDef' object has no attribute 'value' (line 1827)
    inst.__class__ = UndefinedName   # astroid.exceptions.NameInferenceError (line 483)
```

This is the remaining family of #7467: the fix for that issue added the tuple-unpacking branch, but only for a literal right-hand side in a plain `Assign`, and the slots code path was not covered.

### Configuration

```ini
# none needed; reproduces with an empty configuration
```

### Command used

```shell
pylint --disable=all --enable=invalid-class-object,assigning-non-slot crash_for.py
```

### Pylint output

```shell
crash_for.py:1:0: F0002: crash_for.py: Fatal error while checking 'crash_for.py'. Please open an issue in our bug tracker so we address this. ... (astroid-error)
```

(full tracebacks above)

### Expected behavior

No crash. When the value assigned to `__class__` cannot be pinpointed (loop/`with`/comprehension targets, unpacking from a non-literal RHS, bare annotation), the checks should stay quiet like other uninferable cases instead of aborting the whole module; an unresolvable RHS in `_has_same_layout_slots` should get the same answer as any other non-class value (`assigning-non-slot` is still emitted, matching the current behavior for `Uninferable`).

I have a minimal fix with regression tests ready and will open a PR right after this issue.

*This report was prepared with AI assistance as part of a code correctness review; every crash was reproduced locally and each conclusion was reviewed.*

### Pylint version

```shell
pylint 4.1.0-dev0 (main, 4be9585ecfe0f9922917905e7884710baa932886)
astroid 4.3.0
Python 3.13.3 (main, Apr  8 2025, 13:54:08) [Clang 17.0.0 (clang-1700.0.13.3)]
```

Also reproduced on the released pylint 4.0.7 (astroid 4.0.4).

### OS / Environment

macOS 15 (darwin 25.5.0)


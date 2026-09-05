# Crash (astroid-error) in comparison-with-callable when comparing a lambda assigned as a class attribute

### Bug description

`comparison-with-callable` crashes with an `astroid-error` (F0002) when one side of a comparison infers to a **lambda that was assigned as a class attribute** and is accessed through an instance (`self.attr` / `Instance().attr`), i.e. astroid infers it as a `BoundMethod` proxying a `Lambda`:

```python
class C:
    lam = lambda self: 1

    def check(self):
        return self.lam == 1   # crash
```

### Command used

```shell
pylint --disable=all --enable=comparison-with-callable t.py
```

### Pylint output

```
Exception on node <Compare l.5 ...> in file 't.py'
Traceback (most recent call last):
  File ".../pylint/checkers/base/comparison_checker.py", line 287, in _check_callable_comparison
    and "typing._SpecialForm" not in inferred.decoratornames()
                                     ^^^^^^^^^^^^^^^^^^^^^^^
  File ".../astroid/bases.py", line 146, in __getattr__
    return getattr(self._proxied, name)
AttributeError: 'Lambda' object has no attribute 'decoratornames'

t.py:1:0: F0002: ... astroid-error ...
```

### Root cause

In `_check_callable_comparison` (`pylint/checkers/base/comparison_checker.py`):

```python
bare_callables = (nodes.FunctionDef, astroid.BoundMethod)
...
if (
    isinstance(inferred, bare_callables)
    and "typing._SpecialForm" not in inferred.decoratornames()   # <-- here
    and not any(isinstance(x, nodes.Raise) for x in inferred.body)
):
```

For `self.lam`, `safe_infer` returns a `BoundMethod` whose `_proxied` is a `Lambda`. It passes `isinstance(inferred, astroid.BoundMethod)`, but `decoratornames()` is defined on `FunctionDef`, **not** on `Lambda` (`hasattr(nodes.Lambda, "decoratornames")` is `False`), so the proxied attribute lookup raises `AttributeError`.

This is exactly the proxy pitfall called out in the repo's own `AGENTS.md` ("a `BoundMethod` can wrap a `Lambda`, which has no `.decorators`"). The `decoratornames()`/`.body` check was introduced in #11055.

### Two things a fix should be careful about

1. **A naive guard on `decoratornames()` alone still crashes on the next line.** `inferred.body` for a `Lambda` is a *single expression node*, not a list (`isinstance(nodes.Lambda(...).body, list)` is `False`, vs. `True` for `FunctionDef`), so `for x in inferred.body` would then raise `TypeError: '...' object is not iterable`.
2. **Bare lambdas are currently a false negative.** `f = lambda: 1; f == 1` emits nothing, because a `Lambda` is not an instance of `nodes.FunctionDef` (in this astroid, `issubclass(nodes.FunctionDef, nodes.Lambda)` is `False`). If `comparison-with-callable` is meant to cover lambdas, that's a related gap worth deciding on in the same change.

Because (2) is a behaviour decision (should comparing a bare/bound lambda to a non-callable be flagged, or just not crash?), I'm raising this as an issue first rather than sending a PR straight away. Happy to submit the fix once you confirm the intended behaviour — I have a patch and functional-test cases drafted.

### Pylint version

```shell
pylint 4.1.0-dev0
astroid 4.2.0b4
Python 3.12.3
```


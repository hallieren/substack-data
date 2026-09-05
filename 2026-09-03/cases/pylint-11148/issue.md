# `useless-parent-delegation` (W0246) false positive when an override changes a positional-only default

### Bug description

`useless-parent-delegation` (`W0246`) is a false positive when an override changes the default value of a **positional-only** parameter.

```python
class Base:
    def method(self, a=1, /):
        return a


class Child(Base):
    def method(self, a=2, /):        # not useless: default changed 1 -> 2
        return super().method(a)
```

`Child().method()` returns `2` while `Base().method()` returns `1`, so the override is meaningful — but `W0246` fires. The equivalent with a regular positional argument (`def method(self, a=2):`) is correctly **not** flagged.

### Command used

```shell
pylint --disable=all --enable=useless-parent-delegation f.py
```

### Pylint output

```
W0246: Useless parent or super() delegation in method 'method'
```

### Expected behavior

No message — the override changes the default, exactly as the regular-argument equivalent is (correctly) excused.

### Root cause

`pylint/checkers/classes/class_checker.py` — `_has_different_parameters_default_value` iterates `chain(original.args, original.kwonlyargs)` and omits `original.posonlyargs`, so a changed default on a positional-only parameter is never detected.

### Pylint version

```
pylint main (2bfab5f), astroid 4.2.0b3, Python 3.12
```


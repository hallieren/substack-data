# Wrong undefined-variable detection after object is used as metaclass

### Bug description

```python
from foo import bar


class Test:

    def test1(self):

        class A(metaclass=bar.Meta):
            pass


bar.Meta  # Triggers E0602: Undefined variable 'bar' (undefined-variable)
```

What seems to be happening: `bar` is passed as `metaclass` parameter of a class defined inside of a method of another class. This somehow makes it undefined. Because of that using `bar` anywhere else later in the module will trigger an `undefined-variable` error.

### Configuration

```ini

```

### Command used

```shell
pylint -E undefined_var.py
```

### Pylint output

```python
************* Module undefined_var
undefined_var.py:12:0: E0602: Undefined variable 'bar' (undefined-variable)
```

### Expected behavior

`bar` is a well defined object. `undefined-variable` shouldn't be raised.

### Pylint version

```shell
pylint 4.0.4
astroid 4.0.3
Python 3.13

(Also reproducible with earlier versions.)
```

### OS / Environment

Not important.

### Additional dependencies

```python

```

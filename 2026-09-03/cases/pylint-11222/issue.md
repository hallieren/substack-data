# AttributeError: 'UnaryOp' object has no attribute 'value'

### Bug description

```python
# Code from a local fuzzing run

import copy

copy.copy(**{-1: 1})
```

### Configuration

```ini

```

### Command used

```shell
pylint crash.py
```

### Pylint output

```python
Traceback (most recent call last):
  File "pylint/pylint/checkers/stdlib.py", line 658, in _check_shallow_copy_environ
    arg = utils.get_argument_from_call(node, position=0, keyword="x")
  File "pylint/pylint/checkers/utils.py", line 744, in get_argument_from_call
    raise NoSuchArgumentError
pylint.checkers.utils.NoSuchArgumentError

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "pylint/pylint/utils/ast_walker.py", line 87, in walk
    callback(astroid)
    ~~~~~~~~^^^^^^^^^
  File "pylint/pylint/checkers/stdlib.py", line 714, in visit_call
    self._check_shallow_copy_environ(node)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "pylint/pylint/checkers/stdlib.py", line 660, in _check_shallow_copy_environ
    arg = utils.infer_kwarg_from_call(node, keyword="x")
  File "pylint/pylint/checkers/utils.py", line 760, in infer_kwarg_from_call
    if item[0].value == keyword:
       ^^^^^^^^^^^^^
AttributeError: 'UnaryOp' object has no attribute 'value'
```

### Expected behavior

No crash

### Pylint version

```shell
pylint-dev/astroid@5f428849d
pylint-dev/pylint@e95c41667
Python 3.14.6

The crash also affects Pylint 4.0.6
```

### OS / Environment

Arch Linux

### Additional dependencies

```python

```

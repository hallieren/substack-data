# `AttributeError: 'AssignName' object has no attribute 'decorators'` with docparams checker

### Bug description

```python
# Code from a local fuzzing run

class C:
    prop = None

    @prop.setter
    def prop(self, value):
        raise Exception
```

### Configuration

```ini

```

### Command used

```shell
pylint --enable-all-extensions crash.py
```

### Pylint output

```python
Traceback (most recent call last):
  File "pylint/pylint/utils/ast_walker.py", line 87, in walk
    callback(astroid)
    ~~~~~~~~^^^^^^^^^
  File "pylint/pylint/extensions/docparams.py", line 313, in visit_raise
    property_ = utils.get_setters_property(func_node)
  File "pylint/pylint/extensions/_check_docs_utils.py", line 66, in get_setters_property
    if utils.decorated_with_property(attr):
       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "pylint/pylint/checkers/utils.py", line 809, in decorated_with_property
    if not node.decorators:
           ^^^^^^^^^^^^^^^
AttributeError: 'AssignName' object has no attribute 'decorators'
```

### Expected behavior

No crash

### Pylint version

```shell
pylint-dev/astroid@aa860bba
pylint-dev/pylint@95f17c3aa
Python 3.14.6

The crash also affects Pylint 4.0.7
```

### OS / Environment

Arch Linux

### Additional dependencies

```python

```

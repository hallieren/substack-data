# `TypeError: NotImplemented should not be used in a boolean context` in variables checker

### Bug description

```python
# Code from a local fuzzing run

if NotImplemented:
    x = 1
x
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
  File "pylint/pylint/utils/ast_walker.py", line 87, in walk
    callback(astroid)
    ~~~~~~~~^^^^^^^^^
  File "pylint/pylint/checkers/variables.py", line 1702, in visit_name
    self._undefined_and_used_before_checker(node, stmt)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
  File "pylint/pylint/checkers/variables.py", line 1745, in _undefined_and_used_before_checker
    action, nodes_to_consume = self._check_consumer(
                               ~~~~~~~~~~~~~~~~~~~~^
        node, stmt, frame, current_consumer, base_scope_type
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "pylint/pylint/checkers/variables.py", line 1847, in _check_consumer
    found_nodes = current_consumer.get_next_to_consume(node)
  File "pylint/pylint/checkers/variables.py", line 625, in get_next_to_consume
    uncertain_nodes = self._uncertain_nodes_if_tests(found_nodes, node)
  File "pylint/pylint/checkers/variables.py", line 814, in _uncertain_nodes_if_tests
    if self._inferred_to_define_name_raise_or_return(name, outer_if):
       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
  File "pylint/pylint/checkers/variables.py", line 704, in _inferred_to_define_name_raise_or_return
    return self._inferred_to_define_name_raise_or_return_for_if_node(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        name, node
        ^^^^^^^^^^
    )
    ^
  File "pylint/pylint/checkers/variables.py", line 734, in _inferred_to_define_name_raise_or_return_for_if_node
    only_search_else = only_search_else and not val
                                            ^^^^^^^
TypeError: NotImplemented should not be used in a boolean context
```

### Expected behavior

No crash

### Pylint version

```shell
pylint-dev/pylint@734b89873616
pylint-dev/astroid@649ec7d37d182
Python 3.14.4
```

### OS / Environment

Arch Linux

### Additional dependencies

```python

```

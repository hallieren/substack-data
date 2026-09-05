# Add `__suppress_context__` to list of dunders recognized by `W3201: bad-dunder-name` by default

### Current problem

The `bad-dunder-name` warning is very useful and can detect mistyped double-underscore method names in class bodies, for one, and also warns if an unrecognized dunder is used, since those are [reserved for python](https://docs.python.org/3/reference/lexical_analysis.html#reserved-classes-of-identifiers). However, it currently does not appear to recognize `__suppress_context__`, an attribute of instances of `BaseException`, as a valid dunder in exception subclasses, where one may want to override it as a `property`. I acknowledge that this is a niche use case, but it relates to correctness of this rule.

### Desired solution

Mark `__suppress_context__` as a predefined dunder for which `W3201` stays silent.

### Additional context

_No response_

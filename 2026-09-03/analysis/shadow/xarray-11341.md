# xarray-11341 — https://github.com/pydata/xarray/issues/11341

## reference

F2P: ['xarray/tests/test_dataarray.py::TestDataArray::test_selection_multiindex_nested_tuple_level_value']

pico's F2P results: {'xarray/tests/test_dataarray.py::TestDataArray::test_selection_multiindex_nested_tuple_level_value': 'PASSED'}

## pico's final report

Implemented the fix in `/testbed/xarray/core/indexes.py`.

### What changed

In `PandasMultiIndex.sel`, when a tuple label is “nested” (contains a tuple/list/slice element), xarray previously always routed it to `pandas.MultiIndex.get_locs`, which returns a positional array. For a MultiIndex with tuple-valued levels, a full key like `((1, 1), 2)` is exactly the kind of nested tuple pandas also understands as a single exact key via `get_loc` — but `get_locs` made xarray treat it as a sequence, preserving a length‑1 dimension.

The fix now:

- If a nested tuple has the same length as the number of MultiIndex levels, first tries an exact lookup with `get_loc`.
- This returns a scalar (or a duplicate-matching indexer just like the non-tuple-valued-level case), so scalar selections collapse the dimension.
- If no exact match exists, it falls back to the previous `get_locs` behavior, preserving existing support for slices, lists of alternatives, and other sequence-style MultiIndex selections.

### Verification

- The MVCE from the PR now returns a scalar result for the nested tuple case:

  ```python
  nested.dims == ()
  nested.shape == ()
  ```

  matching the behavior of the flat-level MultiIndex.

- Verified tuple-valued partial selections, slice-based selections, and alternative-list selections still behave as before.
- Ran relevant test suites:
  - `xarray/tests/test_indexes.py`
  - `xarray/tests/test_indexing.py`
  - `xarray/tests/test_dataarray.py`
  - `xarray/tests/test_dataset.py` (one unrelated pre-existing `test_repr` failure remains, which also fails without this change).

## pico's patch

```diff
diff --git a/xarray/core/indexes.py b/xarray/core/indexes.py
index 7907f1f5..131939e6 100644
--- a/xarray/core/indexes.py
+++ b/xarray/core/indexes.py
@@ -9,6 +9,7 @@ from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast, overload
 
 import numpy as np
 import pandas as pd
+from pandas.errors import InvalidIndexError
 
 from xarray.core import formatting, nputils, utils
 from xarray.core.coordinate_transform import CoordinateTransform
@@ -1369,7 +1370,19 @@ class PandasMultiIndex(PandasIndex):
 
             elif isinstance(label, tuple):
                 if _is_nested_tuple(label):
-                    indexer = self.index.get_locs(label)
+                    if len(label) == self.index.nlevels:
+                        # A nested tuple whose length matches the number of
+                        # levels can still be an exact key for a MultiIndex
+                        # with tuple-valued levels. Prefer exact lookup (which
+                        # collapses scalar selections), falling back to
+                        # pandas' sequence-based lookup if no exact match is
+                        # found (e.g. slices or lists of alternatives).
+                        try:
+                            indexer = self.index.get_loc(label)
+                        except (KeyError, InvalidIndexError):
+                            indexer = self.index.get_locs(label)
+                    else:
+                        indexer = self.index.get_locs(label)
                 elif len(label) == self.index.nlevels:
                     indexer = self.index.get_loc(label)
                 else:

```

## human fix (merged PR #11348)

```diff
diff --git a/doc/whats-new.rst b/doc/whats-new.rst
index 7a23c055bf5..78acf08218c 100644
--- a/doc/whats-new.rst
+++ b/doc/whats-new.rst
@@ -154,6 +154,9 @@ Deprecations
 Bug Fixes
 ~~~~~~~~~
 
+- Treat a full ``MultiIndex`` key with tuple-valued levels as scalar selection,
+  so ``.sel`` no longer preserves a length-1 dimension for nested tuple keys
+  that identify a single row (:issue:`11341`).
 - :py:meth:`Dataset.drop_encoding` and :py:meth:`DataArray.drop_encoding` no
   longer copy the underlying data, avoiding excessive memory use on large
   datasets (:issue:`11390`, :pull:`11394`).
diff --git a/xarray/core/indexes.py b/xarray/core/indexes.py
index 7907f1f5454..e87c0d5c7ce 100644
--- a/xarray/core/indexes.py
+++ b/xarray/core/indexes.py
@@ -1368,10 +1368,15 @@ def sel(self, labels, method=None, tolerance=None) -> IndexSelResult:
                 indexer = _query_slice(self.index, label, coord_name)
 
             elif isinstance(label, tuple):
-                if _is_nested_tuple(label):
+                if len(label) == self.index.nlevels:
+                    try:
+                        indexer = self.index.get_loc(label)
+                    except (KeyError, TypeError, pd.errors.InvalidIndexError):
+                        if not _is_nested_tuple(label):
+                            raise
+                        indexer = self.index.get_locs(label)
+                elif _is_nested_tuple(label):
                     indexer = self.index.get_locs(label)
-                elif len(label) == self.index.nlevels:
-                    indexer = self.index.get_loc(label)
                 else:
                     levels = [self.index.names[i] for i in range(len(label))]
                     indexer, new_index = self.index.get_loc_level(label, level=levels)

```

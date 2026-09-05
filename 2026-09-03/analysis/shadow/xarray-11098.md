# xarray-11098 — https://github.com/pydata/xarray/issues/11098

## reference

F2P: ['xarray/tests/test_indexing.py::test_pandas_StringDtype_index_coerces_to_numpy']

pico's F2P results: {'xarray/tests/test_indexing.py::test_pandas_StringDtype_index_coerces_to_numpy': 'FAILED'}

## pico's final report

Implemented the fix in `/testbed/xarray/core/indexes.py`.

What changed:
- `PandasIndex.__init__` now validates explicitly provided `coord_dtype` values.
- If a dtype is neither a supported pandas extension dtype nor a valid NumPy dtype (e.g. `pandas.StringDtype`, which pandas 3 now uses by default for string `Index` objects), xarray falls back to a NumPy-compatible dtype derived from the underlying pandas index (`get_valid_numpy_dtype`), typically `object`.

This prevents `PandasIndex.create_variables()` from later passing `StringDtype` into `PandasIndexingAdapter`, where `np.dtype(StringDtype)` raised:

```
TypeError: Cannot interpret '<StringDtype(na_value=nan)>' as a data type
```

Verification:
- The MCVE from the issue now succeeds and produces the pandas-2-compatible result:

```
Coordinates:
  * y        (y) object 16B 'y1' 'y2'
  * x        (x) <U2 16B 'x1' 'x2'
```

- Existing relevant test suites pass:
  - `xarray/tests/test_indexes.py` — 74 passed, 2 skipped
  - `xarray/tests/test_concat.py` — 138 passed, 3 skipped

## pico's patch

```diff
diff --git a/xarray/core/indexes.py b/xarray/core/indexes.py
index 74729d8e..038e3dcf 100644
--- a/xarray/core/indexes.py
+++ b/xarray/core/indexes.py
@@ -26,6 +26,7 @@ from xarray.core.utils import (
     is_allowed_extension_array_dtype,
     is_dict_like,
     is_scalar,
+    is_valid_numpy_dtype,
 )
 
 if TYPE_CHECKING:
@@ -675,6 +676,13 @@ class PandasIndex(Index):
                 coord_dtype = index.dtype
             else:
                 coord_dtype = get_valid_numpy_dtype(index)
+        elif not is_allowed_extension_array_dtype(
+            coord_dtype
+        ) and not is_valid_numpy_dtype(coord_dtype):
+            # pandas 3 uses StringDtype by default for str indices, but xarray
+            # does not support this pandas extension dtype: fall back to a
+            # numpy-compatible dtype (usually object) for the coordinate.
+            coord_dtype = get_valid_numpy_dtype(index)
         self.coord_dtype = coord_dtype
 
     def _replace(self, index, dim=None, coord_dtype=None):

```

## human fix (merged PR #11102)

```diff
diff --git a/doc/whats-new.rst b/doc/whats-new.rst
index 4b50f51cf61..93582f6b261 100644
--- a/doc/whats-new.rst
+++ b/doc/whats-new.rst
@@ -71,6 +71,9 @@ Bug Fixes
 - Ensure the :py:class:`~xarray.groupers.SeasonResampler` preserves the datetime
   unit of the underlying time index when resampling (:issue:`11048`,
   :pull:`11049`). By `Spencer Clark <https://github.com/spencerkclark>`_.
+- Partially support pandas 3 default string indexes by coercing ``pd.StringDtype``
+  to ``np.dtypes.StringDType`` in ``PandasIndexingAdapter`` (:issue:`11098`, :pull:`11102`).
+  By `Julia Signell <https://github.com/jsignell>`_.
 
 Documentation
 ~~~~~~~~~~~~~
diff --git a/xarray/core/indexing.py b/xarray/core/indexing.py
index f5e3183fd8c..b1e01a3f79a 100644
--- a/xarray/core/indexing.py
+++ b/xarray/core/indexing.py
@@ -16,6 +16,7 @@
 from numpy.typing import DTypeLike
 from packaging.version import Version
 
+from xarray.compat.npcompat import HAS_STRING_DTYPE
 from xarray.core import duck_array_ops
 from xarray.core.coordinate_transform import CoordinateTransform
 from xarray.core.nputils import NumpyVIndexAdapter
@@ -1916,6 +1917,8 @@ def __init__(
                 self._dtype = get_valid_numpy_dtype(array)
         elif is_allowed_extension_array_dtype(dtype):
             self._dtype = cast(pd.api.extensions.ExtensionDtype, dtype)
+        elif HAS_STRING_DTYPE and isinstance(dtype, pd.StringDtype):
+            self._dtype = np.dtypes.StringDType(na_object=dtype.na_value)
         else:
             self._dtype = np.dtype(cast(DTypeLike, dtype))
 

```

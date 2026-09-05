# xarray-11148-nofix — https://github.com/pydata/xarray/issues/11148

## reference

F2P: []

pico's F2P results: {}

## pico's final report

Implemented the fix in `/testbed`:

- Changed `Dataset.copy` and `Dataset._copy` default for `deep` from `False` to `True`, so `Dataset.copy()` now matches `DataArray.copy()` (both deep-copy by default).
- Updated internal `Dataset.copy()` call sites that were relying on the old shallow-by-default behavior to explicitly use `deep=False`, preserving their previous no-copy/shallow semantics (e.g. `set_coords`, `reset_coords`, `transpose`, `assign`, `concat`, and `unify_chunks`).

Verified with the relevant test modules; the copy behavior is now consistent between `Dataset` and `DataArray`.

## pico's patch

```diff
diff --git a/xarray/core/dataset.py b/xarray/core/dataset.py
index 054668a0..f4f937d0 100644
--- a/xarray/core/dataset.py
+++ b/xarray/core/dataset.py
@@ -1026,7 +1026,7 @@ class Dataset(
         else:
             return replaced
 
-    def copy(self, deep: bool = False, data: DataVars | None = None) -> Self:
+    def copy(self, deep: bool = True, data: DataVars | None = None) -> Self:
         """Returns a copy of this dataset.
 
         If `deep=True`, a deep copy is made of each of the component variables.
@@ -1039,9 +1039,9 @@ class Dataset(
 
         Parameters
         ----------
-        deep : bool, default: False
+        deep : bool, default: True
             Whether each component variable is loaded into memory and copied onto
-            the new object. Default is False.
+            the new object. Default is True.
         data : dict-like or None, optional
             Data to use in the new object. Each item in `data` must have same
             shape as corresponding data variable in original. When `data` is
@@ -1127,7 +1127,7 @@ class Dataset(
 
     def _copy(
         self,
-        deep: bool = False,
+        deep: bool = True,
         data: DataVars | None = None,
         memo: dict[int, Any] | None = None,
     ) -> Self:
@@ -1850,7 +1850,7 @@ class Dataset(
         else:
             names = list(names)
         self._assert_all_in_dataset(names)
-        obj = self.copy()
+        obj = self.copy(deep=False)
         obj._coord_names.update(names)
         return obj
 
@@ -1944,7 +1944,7 @@ class Dataset(
                 raise ValueError(
                     f"cannot remove index coordinates with reset_coords: {bad_coords}"
                 )
-        obj = self.copy()
+        obj = self.copy(deep=False)
         obj._coord_names.difference_update(names)
         if drop:
             for name in names:
@@ -6259,7 +6259,7 @@ class Dataset(
         if len(dim) != 0:
             _ = list(infix_dims(dim, self.dims, missing_dims))
 
-        ds = self.copy()
+        ds = self.copy(deep=False)
         for name, var in self._variables.items():
             var_dims = tuple(d for d in dim if d in (var.dims + (...,)))
             ds._variables[name] = var.transpose(*var_dims)
@@ -7090,7 +7090,7 @@ class Dataset(
 
         """
         variables = either_dict_or_kwargs(variables, variables_kwargs, "assign")
-        data = self.copy()
+        data = self.copy(deep=False)
 
         # do all calculations first...
         results: CoercibleMapping = data._calc_assign_results(variables)
diff --git a/xarray/structure/chunks.py b/xarray/structure/chunks.py
index 1fba9753..6b4aa27b 100644
--- a/xarray/structure/chunks.py
+++ b/xarray/structure/chunks.py
@@ -154,7 +154,7 @@ def unify_chunks(*objects: Dataset | DataArray) -> tuple[Dataset | DataArray, ..
 
     # Convert all objects to datasets
     datasets = [
-        obj._to_temp_dataset() if isinstance(obj, DataArray) else obj.copy()
+        obj._to_temp_dataset() if isinstance(obj, DataArray) else obj.copy(deep=False)
         for obj in objects
     ]
 
diff --git a/xarray/structure/concat.py b/xarray/structure/concat.py
index 9609dbcb..c00dd26a 100644
--- a/xarray/structure/concat.py
+++ b/xarray/structure/concat.py
@@ -640,7 +640,7 @@ def _dataset_concat(
     dim_name, index = _calc_concat_dim_index(dim)
 
     # Make sure we're working on a copy (we'll be loading variables)
-    datasets = [ds.copy() for ds in datasets]
+    datasets = [ds.copy(deep=False) for ds in datasets]
     datasets = list(
         align(
             *datasets, join=join, copy=False, exclude=[dim_name], fill_value=fill_value

```

## human fix (merged PR #None)

```diff

```

## maintainers' ruling

[jsignell 2026-02-09] Thanks for pointing this out! This is a super old part of xarray (came in on https://github.com/pydata/xarray/pull/71) and there has been this discrepancy from the beginning. I can see why it would make sense to default to a shallow copy for Dataset (where you might just want to change the names of the variables or something) whereas for DataArray (where you are more likely to be manipulating the data) it makes sense to default to deep. So the current defaults might result in the fewest surprises for users.

Since this would be a breaking change and it's not totally clear to me that the current behavior is more surprising than the proposed I am leaning towards not making this change.


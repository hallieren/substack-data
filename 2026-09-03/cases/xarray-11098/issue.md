# "TypeError: Cannot interpret '<StringDtype(na_value=nan)>' as a data type" with pandas 3.0.0

### What happened?

[Pandas 3.0.0 was released yesterday](https://pandas.pydata.org/pandas-docs/stable/whatsnew/v3.0.0.html).

The MCVE below gives an exception like:
```py
Traceback (most recent call last):
  File "/home/khaeru/vc/genno/script.py", line 18, in <module>
    print(xr.concat([da, da], dim=pd.Index(["y1", "y2"], name="y")))
          ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/khaeru/.cache/uv/environments-v2/script-7d51600a4b1e4ec0/lib/python3.14/site-packages/xarray/structure/concat.py", line 311, in concat
    return _dataarray_concat(
        objs,
    ...<8 lines>...
        create_index_for_new_dim=create_index_for_new_dim,
    )
  File "/home/khaeru/.cache/uv/environments-v2/script-7d51600a4b1e4ec0/lib/python3.14/site-packages/xarray/structure/concat.py", line 907, in _dataarray_concat
    ds = _dataset_concat(
        datasets,
    ...<8 lines>...
        create_index_for_new_dim=create_index_for_new_dim,
    )
  File "/home/khaeru/.cache/uv/environments-v2/script-7d51600a4b1e4ec0/lib/python3.14/site-packages/xarray/structure/concat.py", line 852, in _dataset_concat
    index_vars = index.create_variables()
  File "/home/khaeru/.cache/uv/environments-v2/script-7d51600a4b1e4ec0/lib/python3.14/site-packages/xarray/core/indexes.py", line 799, in create_variables
    data = PandasIndexingAdapter(self.index, dtype=self.coord_dtype)
  File "/home/khaeru/.cache/uv/environments-v2/script-7d51600a4b1e4ec0/lib/python3.14/site-packages/xarray/core/indexing.py", line 1920, in __init__
    self._dtype = np.dtype(cast(DTypeLike, dtype))
                  ~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: Cannot interpret '<StringDtype(na_value=nan)>' as a data type
```

### What did you expect to happen?

With `"pandas < 3"` (instead of `>= 3`) in the header comment, the script gives:
```
…
xarray: 2025.12.1.dev39+g49ec51646
pandas: 2.3.3
…
<xarray.DataArray (y: 2, x: 2)> Size: 32B
array([[0, 1],
       [0, 1]])
Coordinates:
  * y        (y) object 16B 'y1' 'y2'
  * x        (x) <U2 16B 'x1' 'x2'
```

### Minimal Complete Verifiable Example

```Python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas >= 3",
#   "xarray[complete]@git+https://github.com/pydata/xarray.git@main",
# ]
# ///

import pandas as pd
import xarray as xr

xr.show_versions()

# Create a DataArray
da = xr.DataArray([0, 1], coords={"x": ["x1", "x2"]})

# Concatenate along a new dimension by giving a pd.Index
print(xr.concat([da, da], dim=pd.Index(["y1", "y2"], name="y")))
```

### Steps to reproduce

`uv run issue.py`

### MVCE confirmation

- [x] Minimal example — the example is as focused as reasonably possible to demonstrate the underlying issue in xarray.
- [x] Complete example — the example is self-contained, including all data and the text of any traceback.
- [x] Verifiable example — the example copy & pastes into an IPython prompt or [Binder notebook](https://mybinder.org/v2/gh/pydata/xarray/main?urlpath=lab/tree/doc/examples/blank_template.ipynb), returning the result.
- [x] New issue — a search of GitHub Issues suggests this is not a duplicate.
- [x] Recent environment — the issue occurs with the latest version of xarray and its dependencies.

### Relevant log output

None; see traceback above.

### Anything else we need to know?

_No response_

### Environment

<details>

```
INSTALLED VERSIONS
------------------
commit: None
python: 3.14.0 (main, Oct  7 2025, 15:35:21) [Clang 20.1.4 ]
python-bits: 64
OS: Linux
OS-release: 6.17.0-8-generic
machine: x86_64
processor: x86_64
byteorder: little
LC_ALL: None
LANG: en_CA.UTF-8
LOCALE: ('en_CA', 'UTF-8')
libhdf5: 1.14.6
libnetcdf: 4.9.3

xarray: 2025.12.1.dev39+g49ec51646
pandas: 3.0.0
numpy: 2.3.5
scipy: 1.17.0
netCDF4: 1.7.4
pydap: 3.5.8
h5netcdf: None
h5py: None
zarr: 3.1.5
cftime: 1.6.5
nc_time_axis: 1.4.1
iris: None
bottleneck: 1.6.0
dask: 2026.1.1
distributed: 2026.1.1
matplotlib: 3.10.8
cartopy: 0.25.0
seaborn: 0.13.2
numbagg: 0.9.4
fsspec: 2026.1.0
cupy: None
pint: None
sparse: 0.17.0
flox: 0.10.8
numpy_groupies: 0.11.3
setuptools: None
pip: None
conda: None
pytest: None
mypy: None
IPython: None
sphinx: None
```
</details>

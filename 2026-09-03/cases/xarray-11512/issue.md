# Transposing a `CoordinateTransformIndex`-backed array produces wrong coordinate shape

### What happened?

Transposing a DataArray/Dataset whose coordinates are backed by a `CoordinateTransformIndex` leaves the lazy coordinate variable with a stale `.shape`: it still reports the pre-transpose shape instead of the shape implied by the new dimension order. This is invisible when all dimensions happen to have equal length, but becomes an obvious, reproducible failure once dimension sizes differ.

The stale shape then propagates into `.sel()`, which raises a spurious `ValueError` about "conflicting sizes" on a DataArray/Dataset that was never touched in an inconsistent way by the user.

### What did you expect to happen?

- `coordinate.shape` should equal expected_shape, i.e. `(4, 2, 3)`, matching `coordinate.dims == ("i", "k", "j")`.
- `.sel(..., method="nearest")` on the transposed array should succeed and return the correct value, just as it does before transposing.

### Minimal Complete Verifiable Example

```Python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "xarray[complete]@git+https://github.com/pydata/xarray.git@main",
# ]
# ///
import numpy as np
import xarray as xr
from xarray.indexes import CoordinateTransform, CoordinateTransformIndex

xr.show_versions()


class AffineTransform(CoordinateTransform):
    """Three-dimensional oblique affine coordinate transform."""

    def __init__(self) -> None:
        super().__init__(
            coord_names=("z", "y", "x"),
            dim_size={"k": 2, "j": 3, "i": 4},
        )
        self.affine = np.array(
            [
                [1.0, 0.1, 0.01],
                [0.2, 1.0, 0.02],
                [0.03, 0.04, 1.0],
            ]
        )

    def forward(self, dim_positions: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        positions = np.stack([dim_positions[dim] for dim in self.dims], axis=0)
        world = np.einsum("ab,b...->a...", self.affine, positions)
        return dict(zip(self.coord_names, world, strict=True))

    def reverse(self, coord_labels: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        world = np.stack([coord_labels[name] for name in self.coord_names], axis=0)
        positions = np.einsum("ab,b...->a...", np.linalg.inv(self.affine), world)
        return dict(zip(self.dims, positions, strict=True))

    def equals(
        self, other: CoordinateTransform, *, exclude: frozenset[str] | None = None
    ) -> bool:
        return isinstance(other, AffineTransform) and np.array_equal(
            self.affine, other.affine
        )


transform = AffineTransform()
data = xr.DataArray(
    np.arange(2 * 3 * 4).reshape(2, 3, 4),
    dims=transform.dims,
    coords=xr.Coordinates.from_xindex(CoordinateTransformIndex(transform)),
)

transposed = data.transpose("i", "k", "j")
coordinate = transposed.coords["z"]
expected_shape = tuple(transposed.sizes[dim] for dim in coordinate.dims)

print(f"coordinate dims:  {coordinate.dims}")
print(f"coordinate shape: {coordinate.shape}")  # (2, 3, 4)  <- stale
print(f"expected shape:   {expected_shape}")  # (4, 2, 3)  <- correct

point = {"k": 1.0, "j": 2.0, "i": 3.0}
world = transform.forward({dim: np.asarray([point[dim]]) for dim in transform.dims})
transposed.sel(
    **{name: xr.Variable("point", values) for name, values in world.items()},
    method="nearest",
)
```

### Steps to reproduce

_No response_

### MVCE confirmation

- [x] Minimal example — the example is as focused as reasonably possible to demonstrate the underlying issue in xarray.
- [x] Complete example — the example is self-contained, including all data and the text of any traceback.
- [x] Verifiable example — the example copy & pastes into an IPython prompt or [Binder notebook](https://mybinder.org/v2/gh/pydata/xarray/main?urlpath=lab/tree/doc/examples/blank_template.ipynb), returning the result.
- [x] New issue — a search of GitHub Issues suggests this is not a duplicate.
- [x] Recent environment — the issue occurs with the latest version of xarray and its dependencies.

### Relevant log output

```Python
coordinate dims:  ('i', 'k', 'j')
coordinate shape: (2, 3, 4)
expected shape:   (4, 2, 3)
ValueError: conflicting sizes for dimension 'i': length 4 on <this-array> and length 2 on {'i': 'z', 'k': 'z', 'j': 'z'}
```

### Anything else we need to know?

`CoordinateTransformIndexingAdapter.transpose()` (in `xarray/core/indexing.py`) correctly builds a new adapter with reordered `self._dims`:

```python
def transpose(self, order: Iterable[int]) -> Self:
    new_dims = tuple(self._dims[i] for i in order)
    return type(self)(self._transform, self._coord_name, new_dims)
```

but `shape` ignores `self._dims` entirely and just reads the transform's `dim_size` dict in its original insertion order:

```python
@property
def shape(self) -> tuple[int, ...]:
    return tuple(self._transform.dim_size.values())
```

Because `dim_size.values()` order never changes, `.shape` stays fixed at the original dimension order regardless of how the adapter has been transposed. With equal-length dimensions this is silently wrong (the tuple happens to look the same); with unequal-length dimensions it produces a directly observable shape mismatch, which then breaks `.sel()` via alignment.

### Environment

<details>
INSTALLED VERSIONS                                                                                                                                                                    ------------------                                                                                                                                                                    commit: None                                                                                                                                                                          python: 3.14.3 (main, Mar 24 2026, 22:50:36) [Clang 22.1.1 ]                                                                                                                          python-bits: 64
OS: Linux
OS-release: 7.1.6-arch1-1
machine: x86_64
processor:
byteorder: little
LC_ALL: en_US.UTF-8
LANG: en_US.UTF-8
LOCALE: ('en_US', 'UTF-8')
libhdf5: 1.14.6
libnetcdf: 4.9.3

xarray: 2026.7.1.dev24+g80b6a9260
pandas: 3.0.5
numpy: 2.5.2
scipy: 1.18.0
netCDF4: 1.7.4
pydap: 3.5.10
h5netcdf: 1.8.1
h5py: 3.16.0
zarr: 3.3.0
cftime: 1.6.5
nc_time_axis: 1.4.1
iris: None
bottleneck: 1.6.0
dask: 2026.7.1
distributed: 2026.7.1
matplotlib: 3.11.1
cartopy: 0.25.0
seaborn: 0.13.2
numbagg: 0.9.4
fsspec: 2026.7.0
cupy: None
pint: None
sparse: 0.19.1
flox: 0.11.2
numpy_groupies: 0.11.3
setuptools: None
pip: None
conda: None
pytest: None
mypy: None
IPython: None
sphinx: None
None
</details>

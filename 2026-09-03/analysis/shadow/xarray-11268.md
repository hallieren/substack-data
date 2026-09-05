# xarray-11268 — https://github.com/pydata/xarray/issues/11268

## reference

F2P: ['xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_field_access[day_of_week]', 'xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_field_access[day_of_year]', 'xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_field_access[daysinmonth]', 'xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_field_access[weekday]', 'xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_field_access[weekofyear]', 'xarray/tests/test_dataarray.py::TestDataArray::test_virtual_time_components', 'xarray/tests/test_dataset.py::TestDataset::test_sel', 'xarray/tests/test_dataset.py::TestDataset::test_slice_virtual_variable', 'xarray/tests/test_dataset.py::TestDataset::test_virtual_variables_time']

pico's F2P results: {'xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_field_access[day_of_week]': 'FAILED', 'xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_field_access[day_of_year]': 'FAILED', 'xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_field_access[daysinmonth]': 'FAILED', 'xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_field_access[weekday]': 'FAILED', 'xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_field_access[weekofyear]': 'FAILED', 'xarray/tests/test_dataarray.py::TestDataArray::test_virtual_time_components': 'FAILED', 'xarray/tests/test_dataset.py::TestDataset::test_sel': 'FAILED', 'xarray/tests/test_dataset.py::TestDataset::test_slice_virtual_variable': 'FAILED', 'xarray/tests/test_dataset.py::TestDataset::test_virtual_variables_time': 'FAILED'}

## pico's final report

I've fixed the pandas 4.0 deprecation warnings originating from xarray code.

## Changes made

### `xarray/core/accessor_dt.py`
- Added `_PANDAS_DATETIME_FIELD_RENAMES`, mapping pandas' deprecated datetime field names to their non-deprecated snake_case replacements:
  - `dayofweek`/`weekday` → `day_of_week`
  - `dayofyear` → `day_of_year`
  - `daysinmonth` → `days_in_month`
- `_access_through_series` now applies this mapping before calling `Series.dt.<field>`. xarray keeps its public `.dt.dayofweek` / `.dt.dayofyear` / etc. API unchanged, but internally calls the modern pandas accessors, avoiding `Pandas4Warning`/`FutureWarning` from pandas 4.0.
- The CFTimeIndex path is untouched because cftime fields aren't affected by pandas deprecations.

### `xarray/coding/cftime_offsets.py`
- Added `_get_days_in_month(date)` helper that uses `.days_in_month` when available (pandas `Timestamp`) and falls back to `.daysinmonth` for `cftime.datetime` objects (which only expose `daysinmonth`).
- `date_range_like` now uses this helper at the month-end detection/replacement logic, so `Timestamp.daysinmonth` (deprecated in pandas 4.0) is no longer called when the source or target dates are pandas `Timestamp`s, while cftime behavior is preserved.

These changes cover the warnings raised through xarray code paths: `.dt` field access (`dayofweek`, `weekday`, `dayofyear`, `daysinmonth`), dask field access, virtual time components (`time.dayofyear`), calendar conversion helpers (`convert_calendar` → `dt.dayofyear`), and `date_range_like` (`Timestamp.daysinmonth`).

I verified the relevant test modules still pass:
- `test_accessor_dt.py`
- `test_calendar_ops.py`
- virtual-variable tests in `test_dataset.py` / `test_dataarray.py`
- `date_range_like` with several end-of-month frequencies under `-W error`

I also simulated pandas 4.0 by making the deprecated accessors raise and confirmed xarray no longer uses them in those paths.

## pico's patch

```diff
diff --git a/xarray/coding/cftime_offsets.py b/xarray/coding/cftime_offsets.py
index 154c3919..f0bae116 100644
--- a/xarray/coding/cftime_offsets.py
+++ b/xarray/coding/cftime_offsets.py
@@ -234,6 +234,19 @@ class Tick(BaseCFTimeOffset):
         raise NotImplementedError
 
 
+def _get_days_in_month(date):
+    """Return the number of days in the month containing ``date``.
+
+    Works for both :py:class:`cftime.datetime` objects, which only expose
+    ``daysinmonth``, and ``pandas.Timestamp`` objects, which prefer the
+    non-deprecated ``days_in_month`` attribute.
+    """
+    days_in_month = getattr(date, "days_in_month", None)
+    if days_in_month is None:
+        days_in_month = date.daysinmonth
+    return days_in_month
+
+
 def _get_day_of_month(other, day_option: DayOption) -> int:
     """Find the day in `other`'s month that satisfies a BaseCFTimeOffset's
     onOffset policy, as described by the `day_option` argument.
@@ -1623,10 +1636,10 @@ def date_range_like(source, calendar, use_cftime=None):
     end = convert_time_or_go_back(source_end, date_type)
 
     # For the cases where the source ends on the end of the month, we expect the same in the new calendar.
-    if source_end.day == source_end.daysinmonth and isinstance(
+    if source_end.day == _get_days_in_month(source_end) and isinstance(
         freq_as_offset, YearEnd | QuarterEnd | MonthEnd | Day
     ):
-        end = end.replace(day=end.daysinmonth)
+        end = end.replace(day=_get_days_in_month(end))
 
     return date_range(
         start=start.isoformat(),
diff --git a/xarray/core/accessor_dt.py b/xarray/core/accessor_dt.py
index 5e0d0fc5..79d5445c 100644
--- a/xarray/core/accessor_dt.py
+++ b/xarray/core/accessor_dt.py
@@ -29,6 +29,18 @@ if TYPE_CHECKING:
     from xarray.core.types import CFCalendar
 
 
+# pandas deprecated some aliases of datetime properties in favor of
+# snake_case names (e.g. ``DatetimeIndex.dayofyear`` -> ``day_of_year``).
+# xarray keeps exposing the historical names as public API, but calls the
+# non-deprecated pandas accessors internally to avoid deprecation warnings.
+_PANDAS_DATETIME_FIELD_RENAMES = {
+    "dayofweek": "day_of_week",
+    "weekday": "day_of_week",
+    "dayofyear": "day_of_year",
+    "daysinmonth": "days_in_month",
+}
+
+
 def _season_from_months(months):
     """Compute season (DJF, MAM, JJA, SON) from month ordinal"""
     # TODO: Move "season" accessor upstream into pandas
@@ -99,6 +111,7 @@ def _access_through_series(values, name):
         # isocalendar returns iso- year, week, and weekday -> reshape
         return field_values.T.reshape(3, *values.shape)
     else:
+        name = _PANDAS_DATETIME_FIELD_RENAMES.get(name, name)
         field_values = getattr(values_as_series.dt, name).values
 
     return field_values.reshape(values.shape)

```

## human fix (merged PR #11270)

```diff
diff --git a/_stubtest/allowlist.txt b/_stubtest/allowlist.txt
index dcf7d3ba337..eabb0d7999b 100644
--- a/_stubtest/allowlist.txt
+++ b/_stubtest/allowlist.txt
@@ -107,7 +107,9 @@ xarray\.core\.dataset\.DatasetResample$
 
 xarray\.core\.(dataarray|dataset)\.CFTimeIndex\.date_type$
 xarray\.core\.(dataarray|dataset)\.CFTimeIndex\.day$
+xarray\.core\.(dataarray|dataset)\.CFTimeIndex\.day_of_week$
 xarray\.core\.(dataarray|dataset)\.CFTimeIndex\.dayofweek$
+xarray\.core\.(dataarray|dataset)\.CFTimeIndex\.day_of_year$
 xarray\.core\.(dataarray|dataset)\.CFTimeIndex\.dayofyear$
 xarray\.core\.(dataarray|dataset)\.CFTimeIndex\.days_in_month$
 xarray\.core\.(dataarray|dataset)\.CFTimeIndex\.hour$
diff --git a/doc/api-hidden.rst b/doc/api-hidden.rst
index cabca85cdbc..df851eec990 100644
--- a/doc/api-hidden.rst
+++ b/doc/api-hidden.rst
@@ -114,7 +114,9 @@
    core.accessor_dt.DatetimeAccessor.date
    core.accessor_dt.DatetimeAccessor.day
    core.accessor_dt.DatetimeAccessor.dayofweek
+   core.accessor_dt.DatetimeAccessor.day_of_week
    core.accessor_dt.DatetimeAccessor.dayofyear
+   core.accessor_dt.DatetimeAccessor.day_of_year
    core.accessor_dt.DatetimeAccessor.days_in_month
    core.accessor_dt.DatetimeAccessor.daysinmonth
    core.accessor_dt.DatetimeAccessor.hour
@@ -409,6 +411,8 @@
    CFTimeIndex.ceil
    CFTimeIndex.contains
    CFTimeIndex.copy
+   CFTimeIndex.day_of_week
+   CFTimeIndex.day_of_year
    CFTimeIndex.days_in_month
    CFTimeIndex.delete
    CFTimeIndex.difference
diff --git a/doc/api/dataarray.rst b/doc/api/dataarray.rst
index 9d4e81c8677..e742a1a2ff5 100644
--- a/doc/api/dataarray.rst
+++ b/doc/api/dataarray.rst
@@ -272,8 +272,10 @@ Datetimelike properties
    DataArray.dt.second
    DataArray.dt.microsecond
    DataArray.dt.nanosecond
+   DataArray.dt.day_of_week
    DataArray.dt.dayofweek
    DataArray.dt.weekday
+   DataArray.dt.day_of_year
    DataArray.dt.dayofyear
    DataArray.dt.quarter
    DataArray.dt.days_in_month
diff --git a/doc/getting-started-guide/why-xarray.rst b/doc/getting-started-guide/why-xarray.rst
index 0dc3586fc34..11fca4aeb67 100644
--- a/doc/getting-started-guide/why-xarray.rst
+++ b/doc/getting-started-guide/why-xarray.rst
@@ -28,7 +28,7 @@ powerful and concise interface. For example:
    dimensions (array broadcasting) based on dimension names, not shape.
 -  Easily use the `split-apply-combine <https://vita.had.co.nz/papers/plyr.pdf>`_
    paradigm with ``groupby``:
-   ``x.groupby('time.dayofyear').mean()``.
+   ``x.groupby('time.day_of_year').mean()``.
 -  Database-like alignment based on coordinate labels that smoothly
    handles missing values: ``x, y = xr.align(x, y, join='outer')``.
 -  Keep track of arbitrary metadata in the form of a Python dictionary:
diff --git a/doc/user-guide/time-series.rst b/doc/user-guide/time-series.rst
index d3f13c2f03c..bebe55ceca6 100644
--- a/doc/user-guide/time-series.rst
+++ b/doc/user-guide/time-series.rst
@@ -150,15 +150,15 @@ given ``DataArray`` can be quickly computed using a special ``.dt`` accessor.
 
 .. jupyter-execute::
 
-    ds.time.dt.dayofweek
+    ds.time.dt.day_of_week
 
 The ``.dt`` accessor works on both coordinate dimensions as well as
 multi-dimensional data.
 
 Xarray also supports a notion of "virtual" or "derived" coordinates for
 `datetime components`__ implemented by pandas, including "year", "month",
-"day", "hour", "minute", "second", "dayofyear", "week", "dayofweek", "weekday"
-and "quarter":
+"day", "hour", "minute", "second", "day_of_year", "week", "day_of_week", and
+"quarter":
 
 __ https://pandas.pydata.org/pandas-docs/stable/api.html#time-date-components
 
@@ -168,7 +168,7 @@ __ https://pandas.pydata.org/pandas-docs/stable/api.html#time-date-components
 
 .. jupyter-execute::
 
-    ds["time.dayofyear"]
+    ds["time.day_of_year"]
 
 For use as a derived coordinate, xarray adds ``'season'`` to the list of
 datetime components supported by pandas:
diff --git a/doc/user-guide/weather-climate.rst b/doc/user-guide/weather-climate.rst
index 3b31fadaa70..7cc1ae69d61 100644
--- a/doc/user-guide/weather-climate.rst
+++ b/doc/user-guide/weather-climate.rst
@@ -184,8 +184,8 @@ For data indexed by a :py:class:`~xarray.CFTimeIndex` xarray currently supports:
 
 - Access of basic datetime components via the ``dt`` accessor (in this case
   just "year", "month", "day", "hour", "minute", "second", "microsecond",
-  "season", "dayofyear", "dayofweek", and "days_in_month") with the addition
-  of "calendar", absent from pandas:
+  "season", "day_of_year", "day_of_week", and "days_in_month") with the
+  addition of "calendar", absent from pandas:
 
 .. jupyter-execute::
 
@@ -201,11 +201,11 @@ For data indexed by a :py:class:`~xarray.CFTimeIndex` xarray currently supports:
 
 .. jupyter-execute::
 
-    da.time.dt.dayofyear
+    da.time.dt.day_of_year
 
 .. jupyter-execute::
 
-    da.time.dt.dayofweek
+    da.time.dt.day_of_week
 
 .. jupyter-execute::
 
diff --git a/doc/whats-new.rst b/doc/whats-new.rst
index b033e04687c..3cd6e877353 100644
--- a/doc/whats-new.rst
+++ b/doc/whats-new.rst
@@ -13,7 +13,16 @@ v2026.05.0 (unreleased)
 
 New Features
 ~~~~~~~~~~~~
-
+- Following pandas, xarray's
+  :py:class:`~xarray.core.accessor_dt.DatetimeAccessor` now supports
+  :py:attr:`~xarray.core.accessor_dt.DatetimeAccessor.day_of_week` and
+  :py:attr:`~xarray.core.accessor_dt.DatetimeAccessor.day_of_year` attributes,
+  which are alternative names for the existing
+  :py:attr:`~xarray.core.accessor_dt.DatetimeAccessor.dayofweek` and
+  :py:attr:`~xarray.core.accessor_dt.DatetimeAccessor.dayofyear` attributes.
+  These alternative attributes have similarly been added to
+  :py:class:`~xarray.CFTimeIndex` (:pull:`11270`). By `Spencer Clark
+  <https://github.com/spencerkclark>`_.
 
 Breaking Changes
 ~~~~~~~~~~~~~~~~
@@ -45,6 +54,16 @@ Bug Fixes
 - Fix ``TypeError: Implicit conversion to a NumPy array is not allowed`` when trying to
   use :py:func:`open_mfdataset` with a backend engine reading to CuPy arrays.
   By `Wei Ji Leong <https://github.com/weiji14>`_.
+- The names of :py:class:`~xarray.DataArray` objects returned by properties of
+  the :py:class:`~xarray.core.accessor_dt.DatetimeAccessor` now always match
+  the property names. Previously properties like
+  :py:attr:`~xarray.core.accessor_dt.DatetimeAccessor.days_in_month`,
+  :py:attr:`~xarray.core.accessor_dt.DatetimeAccessor.weekday`, and
+  :py:attr:`~xarray.core.accessor_dt.DatetimeAccessor.weekofyear` would return
+  :py:class:`~xarray.DataArray` objects named ``"daysinmonth"``,
+  ``"dayofweek"``, and ``"week"``, respectively; now they return objects named
+  ``"days_in_month"``, ``"weekday"``, and ``"weekofyear"`` (:pull:`11270`). By
+  `Spencer Clark <https://github.com/spencerkclark>`_.
 
 Documentation
 ~~~~~~~~~~~~~
diff --git a/xarray/coding/calendar_ops.py b/xarray/coding/calendar_ops.py
index a6f0254a42d..767bf0af2f1 100644
--- a/xarray/coding/calendar_ops.py
+++ b/xarray/coding/calendar_ops.py
@@ -249,7 +249,7 @@ def _interpolate_day_of_year(times, target_calendar):
     source_calendar = times.dt.calendar
     return np.round(
         _days_in_year(times.dt.year, target_calendar)
-        * times.dt.dayofyear
+        * times.dt.day_of_year
         / _days_in_year(times.dt.year, source_calendar)
     ).astype(int)
 
@@ -272,7 +272,7 @@ def _random_day_of_year(time, target_calendar, use_cftime):
         new_doy = np.insert(new_doy, rm_idx - np.arange(5), -1)
         if _days_in_year(year, source_calendar) == 366:
             new_doy = np.insert(new_doy, 60, -1)
-    return new_doy[time.dt.dayofyear - 1]
+    return new_doy[time.dt.day_of_year - 1]
 
 
 def _convert_to_new_calendar_with_new_day_of_year(
diff --git a/xarray/coding/cftime_offsets.py b/xarray/coding/cftime_offsets.py
index 154c39198e0..d9fc4993bd1 100644
--- a/xarray/coding/cftime_offsets.py
+++ b/xarray/coding/cftime_offsets.py
@@ -1623,10 +1623,18 @@ def date_range_like(source, calendar, use_cftime=None):
     end = convert_time_or_go_back(source_end, date_type)
 
     # For the cases where the source ends on the end of the month, we expect the same in the new calendar.
-    if source_end.day == source_end.daysinmonth and isinstance(
+    if isinstance(source_end, pd.Timestamp):
+        source_end_days_in_month = source_end.days_in_month
+    else:
+        source_end_days_in_month = source_end.daysinmonth
+    if isinstance(end, pd.Timestamp):
+        end_days_in_month = end.days_in_month
+    else:
+        end_days_in_month = end.daysinmonth
+    if source_end.day == source_end_days_in_month and isinstance(
         freq_as_offset, YearEnd | QuarterEnd | MonthEnd | Day
     ):
-        end = end.replace(day=end.daysinmonth)
+        end = end.replace(day=end_days_in_month)
 
     return date_range(
         start=start.isoformat(),
diff --git a/xarray/coding/cftimeindex.py b/xarray/coding/cftimeindex.py
index 1aa56317b2d..8a87e26e903 100644
--- a/xarray/coding/cftimeindex.py
+++ b/xarray/coding/cftimeindex.py
@@ -127,7 +127,11 @@ def get_date_field(datetimes, field):
     return np.array([getattr(date, field) for date in datetimes], dtype=np.int64)
 
 
-def _field_accessor(name, docstring=None, min_cftime_version="0.0"):
+def _field_accessor(
+    name: str,
+    docstring: str | None = None,
+    min_cftime_version: str = "0.0",
+):
     """Adapted from pandas.tseries.index._field_accessor"""
 
     def f(self, min_cftime_version=min_cftime_version):
@@ -249,9 +253,21 @@ class CFTimeIndex(pd.Index):
     second = _field_accessor("second", "The seconds of the datetime")
     microsecond = _field_accessor("microsecond", "The microseconds of the datetime")
     dayofyear = _field_accessor(
+        "dayofyr",
+        "The ordinal day of year of the datetime",
+        "1.0.2.1",
+    )
+    dayofweek = _field_accessor(
+        "dayofwk",
+        "The day of week of the datetime",
+        "1.0.2.1",
+    )
+    day_of_year = _field_accessor(
         "dayofyr", "The ordinal day of year of the datetime", "1.0.2.1"
     )
-    dayofweek = _field_accessor("dayofwk", "The day of week of the datetime", "1.0.2.1")
+    day_of_week = _field_accessor(
+        "dayofwk", "The day of week of the datetime", "1.0.2.1"
+    )
     days_in_month = _field_accessor(
         "daysinmonth", "The number of days in the month of the datetime", "1.1.0.0"
     )
diff --git a/xarray/core/accessor_dt.py b/xarray/core/accessor_dt.py
index 5e0d0fc5333..0e5dc19f8e7 100644
--- a/xarray/core/accessor_dt.py
+++ b/xarray/core/accessor_dt.py
@@ -338,8 +338,8 @@ class DatetimeAccessor(TimeAccessor[T_DataArray]):
       * time     (time) datetime64[us] 80B 2000-01-01 2000-01-02 ... 2000-01-10
     >>> ts.dt  # doctest: +ELLIPSIS
     <xarray.core.accessor_dt.DatetimeAccessor object at 0x...>
-    >>> ts.dt.dayofyear
-    <xarray.DataArray 'dayofyear' (time: 10)> Size: 80B
+    >>> ts.dt.day_of_year
+    <xarray.DataArray 'day_of_year' (time: 10)> Size: 80B
     array([ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10])
     Coordinates:
       * time     (time) datetime64[us] 80B 2000-01-01 2000-01-02 ... 2000-01-10
@@ -459,23 +459,45 @@ def weekofyear(self) -> DataArray:
             stacklevel=2,
         )
 
-        weekofyear = self.isocalendar().week
+        return self.isocalendar().week.rename("weekofyear")
 
-        return weekofyear
+    @property
+    def week(self) -> DataArray:
+        "The week ordinal of the year"
+
+        warnings.warn(
+            "dt.weekofyear and dt.week have been deprecated. Please use "
+            "dt.isocalendar().week instead.",
+            FutureWarning,
+            stacklevel=2,
+        )
 
-    week = weekofyear
+        return self.isocalendar().week
+
+    @property
+    def day_of_week(self) -> T_DataArray:
+        """The day of the week with Monday=0, Sunday=6"""
+        return self._date_field("day_of_week", np.int64)
 
     @property
     def dayofweek(self) -> T_DataArray:
         """The day of the week with Monday=0, Sunday=6"""
-        return self._date_field("dayofweek", np.int64)
+        return self._date_field("day_of_week", np.int64).rename("dayofweek")
 
-    weekday = dayofweek
+    @property
+    def weekday(self) -> T_DataArray:
+        """The day of the week with Monday=0, Sunday=6"""
+        return self._date_field("day_of_week", np.int64).rename("weekday")
+
+    @property
+    def day_of_year(self) -> T_DataArray:
+        """The ordinal day of the year"""
+        return self._date_field("day_of_year", np.int64)
 
     @property
     def dayofyear(self) -> T_DataArray:
         """The ordinal day of the year"""
-        return self._date_field("dayofyear", np.int64)
+        return self._date_field("day_of_year", np.int64).rename("dayofyear")
 
     @property
     def quarter(self) -> T_DataArray:
@@ -487,7 +509,10 @@ def days_in_month(self) -> T_DataArray:
         """The number of days in the month"""
         return self._date_field("days_in_month", np.int64)
 
-    daysinmonth = days_in_month
+    @property
+    def daysinmonth(self) -> T_DataArray:
+        """The number of days in the month"""
+        return self._date_field("days_in_month", np.int64).rename("daysinmonth")
 
     @property
     def season(self) -> T_DataArray:
diff --git a/xarray/core/dataarray.py b/xarray/core/dataarray.py
index d0df9bc061b..d5359b36c71 100644
--- a/xarray/core/dataarray.py
+++ b/xarray/core/dataarray.py
@@ -6978,21 +6978,21 @@ def groupby(
                1.826e+03], shape=(1827,))
         Coordinates:
           * time     (time) datetime64[us] 15kB 2000-01-01 2000-01-02 ... 2004-12-31
-        >>> da.groupby("time.dayofyear") - da.groupby("time.dayofyear").mean("time")
+        >>> da.groupby("time.day_of_year") - da.groupby("time.day_of_year").mean("time")
         <xarray.DataArray (time: 1827)> Size: 15kB
         array([-730.8, -730.8, -730.8, ...,  730.2,  730.2,  730.5], shape=(1827,))
         Coordinates:
-          * time       (time) datetime64[us] 15kB 2000-01-01 2000-01-02 ... 2004-12-31
-            dayofyear  (time) int64 15kB 1 2 3 4 5 6 7 8 ... 360 361 362 363 364 365 366
+          * time         (time) datetime64[us] 15kB 2000-01-01 2000-01-02 ... 2004-12-31
+            day_of_year  (time) int64 15kB 1 2 3 4 5 6 7 ... 360 361 362 363 364 365 366
 
         Use a ``Grouper`` object to be more explicit
 
-        >>> da.coords["dayofyear"] = da.time.dt.dayofyear
-        >>> da.groupby(dayofyear=xr.groupers.UniqueGrouper()).mean()
-        <xarray.DataArray (dayofyear: 366)> Size: 3kB
+        >>> da.coords["day_of_year"] = da.time.dt.day_of_year
+        >>> da.groupby(day_of_year=xr.groupers.UniqueGrouper()).mean()
+        <xarray.DataArray (day_of_year: 366)> Size: 3kB
         array([ 730.8,  731.8,  732.8, ..., 1093.8, 1094.8, 1095.5])
         Coordinates:
-          * dayofyear  (dayofyear) int64 3kB 1 2 3 4 5 6 7 ... 361 362 363 364 365 366
+          * day_of_year  (day_of_year) int64 3kB 1 2 3 4 5 6 ... 361 362 363 364 365 366
 
         >>> da = xr.DataArray(
         ...     data=np.arange(12).reshape((4, 3)),

```

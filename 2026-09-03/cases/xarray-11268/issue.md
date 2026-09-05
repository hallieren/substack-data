# ⚠️ Nightly upstream-dev CI failed ⚠️

[Workflow Run URL](https://github.com/pydata/xarray/actions/runs/23825897642)
<details><summary>Python 3.12 Test Summary</summary>

```
xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_field_access[dayofweek]: pandas.errors.Pandas4Warning: DatetimeIndex.dayofweek is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_week instead.
xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_field_access[weekday]: pandas.errors.Pandas4Warning: DatetimeIndex.weekday is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_week instead.
xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_field_access[dayofyear]: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_field_access[daysinmonth]: pandas.errors.Pandas4Warning: DatetimeIndex.daysinmonth is deprecated and will be removed in a future version. Use DatetimeIndex.days_in_month instead.
xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_days_in_year[360_day-360]: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_dask_field_access[dayofweek]: pandas.errors.Pandas4Warning: DatetimeIndex.dayofweek is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_week instead.
xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_dask_field_access[weekday]: pandas.errors.Pandas4Warning: DatetimeIndex.dayofweek is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_week instead.
xarray/tests/test_accessor_dt.py::TestDatetimeAccessor::test_dask_field_access[dayofyear]: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_calendar_ops.py::test_convert_calendar_360_days[year-standard-360_day-D]: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_calendar_ops.py::test_convert_calendar_360_days[year-proleptic_gregorian-360_day-4h]: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_calendar_ops.py::test_convert_calendar_360_days_random: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_calendar_ops.py::test_convert_calendar_missing[standard-noleap-D]: pandas.errors.Pandas4Warning: Timestamp.daysinmonth is deprecated and will be removed in a future version. Use Timestamp.days_in_month instead.
xarray/tests/test_cftime_offsets.py::test_dayofweek_after_cftime[YE]: pandas.errors.Pandas4Warning: DatetimeIndex.dayofweek is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_week instead.
xarray/tests/test_cftime_offsets.py::test_dayofweek_after_cftime[ME]: pandas.errors.Pandas4Warning: DatetimeIndex.dayofweek is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_week instead.
xarray/tests/test_cftime_offsets.py::test_dayofweek_after_cftime[D]: pandas.errors.Pandas4Warning: DatetimeIndex.dayofweek is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_week instead.
xarray/tests/test_cftime_offsets.py::test_dayofyear_after_cftime[YE]: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_cftime_offsets.py::test_dayofyear_after_cftime[ME]: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_cftime_offsets.py::test_dayofyear_after_cftime[D]: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_cftime_offsets.py::test_date_range_like[2020-02-01-4ME-standard-noleap-None-2020-02-28-False]: pandas.errors.Pandas4Warning: Timestamp.daysinmonth is deprecated and will be removed in a future version. Use Timestamp.days_in_month instead.
xarray/tests/test_cftime_offsets.py::test_date_range_like[2020-03-30-ME-360_day-gregorian-False-2020-03-31-True]: pandas.errors.Pandas4Warning: Timestamp.daysinmonth is deprecated and will be removed in a future version. Use Timestamp.days_in_month instead.
xarray/tests/test_cftime_offsets.py::test_date_range_like[2020-03-31-ME-gregorian-360_day-None-2020-03-30-False]: pandas.errors.Pandas4Warning: Timestamp.daysinmonth is deprecated and will be removed in a future version. Use Timestamp.days_in_month instead.
xarray/tests/test_cftime_offsets.py::test_date_range_like[2020-03-31--1ME-gregorian-360_day-None-2020-03-30-False]: pandas.errors.Pandas4Warning: Timestamp.daysinmonth is deprecated and will be removed in a future version. Use Timestamp.days_in_month instead.
xarray/tests/test_cftime_offsets.py::test_date_range_like_no_deprecation[True-YE]: pandas.errors.Pandas4Warning: Timestamp.daysinmonth is deprecated and will be removed in a future version. Use Timestamp.days_in_month instead.
xarray/tests/test_cftime_offsets.py::test_date_range_like_no_deprecation[True-YS]: pandas.errors.Pandas4Warning: Timestamp.daysinmonth is deprecated and will be removed in a future version. Use Timestamp.days_in_month instead.
xarray/tests/test_cftime_offsets.py::test_date_range_like_no_deprecation[True-YE-MAY]: pandas.errors.Pandas4Warning: Timestamp.daysinmonth is deprecated and will be removed in a future version. Use Timestamp.days_in_month instead.
xarray/tests/test_cftime_offsets.py::test_date_range_like_no_deprecation[True-MS]: pandas.errors.Pandas4Warning: Timestamp.daysinmonth is deprecated and will be removed in a future version. Use Timestamp.days_in_month instead.
xarray/tests/test_cftime_offsets.py::test_date_range_like_no_deprecation[True-ME]: pandas.errors.Pandas4Warning: Timestamp.daysinmonth is deprecated and will be removed in a future version. Use Timestamp.days_in_month instead.
xarray/tests/test_cftime_offsets.py::test_date_range_like_no_deprecation[True-QS]: pandas.errors.Pandas4Warning: Timestamp.daysinmonth is deprecated and will be removed in a future version. Use Timestamp.days_in_month instead.
xarray/tests/test_cftime_offsets.py::test_date_range_like_no_deprecation[True-h]: pandas.errors.Pandas4Warning: Timestamp.daysinmonth is deprecated and will be removed in a future version. Use Timestamp.days_in_month instead.
xarray/tests/test_cftime_offsets.py::test_date_range_like_no_deprecation[True-min]: pandas.errors.Pandas4Warning: Timestamp.daysinmonth is deprecated and will be removed in a future version. Use Timestamp.days_in_month instead.
xarray/tests/test_cftime_offsets.py::test_date_range_like_no_deprecation[True-s]: pandas.errors.Pandas4Warning: Timestamp.daysinmonth is deprecated and will be removed in a future version. Use Timestamp.days_in_month instead.
xarray/tests/test_dataarray.py::TestDataArray::test_virtual_time_components: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_dataset.py::TestDataset::test_sel: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_dataset.py::TestDataset::test_virtual_variables_time: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_dataset.py::TestDataset::test_slice_virtual_variable: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_formatting_html.py::test_short_data_repr_html_non_str_keys: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_formatting_html.py::test_repr_of_dataset: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_formatting_html.py::test_repr_text_fallback: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_formatting_html.py::test_repr_of_nonstr_dataset: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_groupby.py::test_weather_data_resample[True]: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
xarray/tests/test_groupby.py::test_weather_data_resample[False]: pandas.errors.Pandas4Warning: DatetimeIndex.dayofyear is deprecated and will be removed in a future version. Use DatetimeIndex.day_of_year instead.
```

</details>


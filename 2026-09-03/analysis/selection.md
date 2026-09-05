# Selection from 453 closed 2026 issues

| reason | n |
|---|---|
| no merged PR closed it | 279 |
| selected | 120 |
| PR changes no source file (docs/meta only) | 22 |
| PR adds no test (no reference) | 22 |
| fixed in another repo (a dependency) | 7 |
| PR source change > 300 lines | 3 |

| repo | selected |
|---|---|
| sympy/sympy | 53 |
| pylint-dev/pylint | 41 |
| pydata/xarray | 22 |
| pallets/flask | 2 |
| mwaskom/seaborn | 1 |
| psf/requests | 1 |

| repo | issue | created | comments | code | pr | src lines | src files | test files | title |
|---|---|---|---|---|---|---|---|---|---|
| sympy/sympy | 30387 | 2026-09-02 | 0 | - | 30392 | 76 | 2 | 4 | Extract scalar coefficients from ArrayTensorProduct with Mat |
| sympy/sympy | 30352 | 2026-08-26 | 0 | y | 30353 | 8 | 1 | 1 | Sign errors in li(z).rewrite(Shi) / Chi and erfi(z).rewrite( |
| sympy/sympy | 30349 | 2026-08-26 | 0 | y | 30350 | 4 | 2 | 1 | airyaiprime(z).rewrite(besseli) uses the wrong Bessel order  |
| sympy/sympy | 30345 | 2026-08-26 | 0 | y | 30347 | 6 | 2 | 1 | owens_t(h, a).evalf() breaks Add cancellation, giving wrong  |
| sympy/sympy | 30343 | 2026-08-25 | 7 | y | 30344 | 4 | 1 | 2 | The printer can crash with `Invalid NaN comparison` on expre |
| sympy/sympy | 30330 | 2026-08-24 | 0 | - | 30331 | 9 | 2 | 1 | subresultants_pg / modified_subresultants_pg crash with Type |
| sympy/sympy | 30314 | 2026-08-21 | 4 | y | 30265 | 92 | 2 | 1 | satask: Use only one SATSolver instance |
| sympy/sympy | 30272 | 2026-08-14 | 1 | y | 30273 | 85 | 1 | 1 | combine_kronecker gives mathematically wrong results for sum |
| sympy/sympy | 30271 | 2026-08-14 | 0 | y | 30274 | 32 | 2 | 2 | array_expressions: latex and pretty printing for ArrayTensor |
| sympy/sympy | 30268 | 2026-08-14 | 0 | y | 30275 | 77 | 1 | 1 | array_expressions: ArrayTensorProduct should pull out scalar |
| sympy/sympy | 30206 | 2026-08-03 | 4 | - | 30265 | 92 | 2 | 1 | satask: Return early on simple cases |
| sympy/sympy | 30198 | 2026-08-03 | 0 | y | 30204 | 86 | 6 | 6 | sympy_to_scipy_sparse use of csr_matrix will be deprecated i |
| sympy/sympy | 30155 | 2026-07-27 | 1 | - | 30265 | 92 | 2 | 1 | satask: Interact wtih SATSolver directly instead of using `s |
| sympy/sympy | 30154 | 2026-07-27 | 1 | - | 30175 | 2 | 1 | 3 | Replace all calls to `ask` with calls to `_ask_recursive` in |
| sympy/sympy | 30148 | 2026-07-26 | 0 | y | 30161 | 135 | 1 | 1 | Using Chebishev substitutions in manualintegrate |
| sympy/sympy | 30121 | 2026-07-23 | 5 | y | 30265 | 92 | 2 | 1 | Add root level inference support to SAT solver |
| sympy/sympy | 30071 | 2026-07-14 | 0 | - | 30079 | 40 | 1 | 1 | integrate `exp(x)*sin(x**2 + x)*cos(x)` hangs indefinitely |
| sympy/sympy | 30031 | 2026-07-07 | 3 | y | 30037 | 212 | 1 | 1 | Improving rational integration in manualintegrate |
| sympy/sympy | 29989 | 2026-06-30 | 0 | y | 29996 | 2 | 2 | 1 | raises AttributeError: `solve_linear(5)` |
| sympy/sympy | 29986 | 2026-06-30 | 4 | y | 30165 | 23 | 1 | 2 | Many rules do not return Piecewise when it should |
| sympy/sympy | 29910 | 2026-06-18 | 3 | y | 29988 | 31 | 1 | 2 | integrate x**2*exp(-x**2)*ln(x) |
| sympy/sympy | 29909 | 2026-06-18 | 1 | y | 29960 | 9 | 1 | 2 | integrate x*exp(x)*erf(x) |
| sympy/sympy | 29908 | 2026-06-18 | 1 | y | 29959 | 4 | 1 | 1 | integrate ln(x)*exp(-x**2) |
| sympy/sympy | 29895 | 2026-06-16 | 1 | y | 30250 | 134 | 1 | 1 | trig_substitution_rule gives the wrong output in manualinteg |
| sympy/sympy | 29851 | 2026-06-07 | 1 | y | 29858 | 3 | 2 | 3 | `z3_satisfiable` gives wrong ans |
| sympy/sympy | 29828 | 2026-06-03 | 3 | y | 29896 | 1 | 1 | 1 | Reducing an integer modulo a Groebner basis gives an error |
| sympy/sympy | 29758 | 2026-05-11 | 0 | y | 29774 | 33 | 1 | 1 | Exponentiating a matrix times scalar should distribute the e |
| sympy/sympy | 29750 | 2026-05-06 | 1 | y | 29780 | 6 | 1 | 1 | raises NotInvertible on a solvable system: `nonlinsolve([2 * |
| sympy/sympy | 29715 | 2026-04-26 | 11 | y | 29719 | 3 | 1 | 2 | Bug of DMP diff |
| sympy/sympy | 29663 | 2026-04-09 | 1 | y | 29712 | 6 | 2 | 1 | Lark parser can't parse implicit multiplication after expone |
| sympy/sympy | 29530 | 2026-03-25 | 2 | y | 29550 | 9 | 1 | 1 | bode_magnitude_numerical_data sometimes blows up |
| sympy/sympy | 29473 | 2026-03-21 | 0 | - | 29474 | 9 | 2 | 1 | The LaTeX printer for ordinals is incorrect |
| sympy/sympy | 29467 | 2026-03-20 | 0 | y | 29479 | 2 | 1 | 1 | Tokens "\\negthinspace" | "\\negmedspace" | "\\negthickspace |
| sympy/sympy | 29433 | 2026-03-17 | 1 | y | 29457 | 6 | 1 | 1 | `ask` incorrectly raises `Inconsistent assumptions` instead  |
| sympy/sympy | 29392 | 2026-03-13 | 0 | y | 29400 | 63 | 4 | 3 | Printing of UnevaluatedExpr is wrong on multiple printers |
| sympy/sympy | 29368 | 2026-03-09 | 0 | y | 29369 | 2 | 1 | 1 | linprog(c) raises misleading `ValueError: must give A and B` |
| sympy/sympy | 29363 | 2026-03-09 | 3 | y | 29370 | 10 | 1 | 1 | Puiseux ring with integer exponents arithmetic not working a |
| sympy/sympy | 29196 | 2026-02-19 | 4 | y | 29592 | 39 | 2 | 1 | test_refine: test_exp contains tests that misleadingly rely  |
| sympy/sympy | 29166 | 2026-02-14 | 3 | y | 29167 | 3 | 2 | 1 | implicit_multiplication_application fails with IndexError ra |
| sympy/sympy | 29117 | 2026-02-06 | 0 | y | 29119 | 3 | 1 | 1 | nP gave 1 as output for invalid k, when k is negative |
| sympy/sympy | 29090 | 2026-02-03 | 1 | y | 29098 | 84 | 3 | 1 | deprecate degree report for numerical expression and non-pol |
| sympy/sympy | 29086 | 2026-02-03 | 1 | y | 29088 | 13 | 1 | 1 | Polygon.centroid returns Point2D(nan, zoo) for zero-area pol |
| sympy/sympy | 29079 | 2026-02-02 | 2 | y | 29160 | 14 | 1 | 1 | LaTeX printing of FreeGroupElements |
| sympy/sympy | 29076 | 2026-02-01 | 0 | y | 29077 | 2 | 1 | 1 | centroid() crashes instead of returning None when passed mix |
| sympy/sympy | 29070 | 2026-02-01 | 0 | - | 29071 | 1 | 1 | 1 | Missing comma in test_direction_cosine in geometry/tests/tes |
| sympy/sympy | 29056 | 2026-01-30 | 5 | y | 29121 | 9 | 2 | 1 | Simplify returns expression with a Dummy variable |
| sympy/sympy | 29043 | 2026-01-28 | 6 | y | 29044 | 5 | 1 | 1 | RecursionError when substituting Points |
| sympy/sympy | 29031 | 2026-01-27 | 0 | y | 29032 | 8 | 1 | 1 | Line.is_parallel raises AttributeError instead of TypeError  |
| sympy/sympy | 29020 | 2026-01-26 | 3 | y | 29033 | 119 | 1 | 1 | Equality of two elements of a free group |
| sympy/sympy | 28975 | 2026-01-20 | 2 | y | 28978 | 12 | 1 | 1 | problem with `limit(2**(1/x), x, 0, dir='-')` and `sp.limit( |
| sympy/sympy | 28970 | 2026-01-18 | 3 | y | 28985 | 8 | 1 | 1 | nonlinsolve crashes with TypeError when using sign functions |
| sympy/sympy | 28945 | 2026-01-15 | 20 | y | 29263 | 132 | 2 | 2 | unhandled by integration routines: `integrate(sqrt(a - x) /  |
| sympy/sympy | 28943 | 2026-01-15 | 0 | y | 28965 | 9 | 3 | 1 | `parse_latex_lark` cannot treat square brackets or curly par |
| pylint-dev/pylint | 11321 | 2026-08-22 | 0 | y | 11322 | 19 | 1 | 2 | False negative: `redundant-unittest-assert` misses `assertEq |
| pylint-dev/pylint | 11315 | 2026-08-19 | 0 | y | 11316 | 19 | 1 | 2 | False positive `bad-string-format-type` for `bool`, `IntEnum |
| pylint-dev/pylint | 11310 | 2026-08-19 | 0 | y | 11311 | 4 | 1 | 2 | False positive `unreachable` after instantiating `_sitebuilt |
| pylint-dev/pylint | 11306 | 2026-08-19 | 0 | y | 11307 | 8 | 1 | 2 | False positive `invalid-*-returned` when returning an instan |
| pylint-dev/pylint | 11295 | 2026-08-18 | 2 | y | 11303 | 21 | 1 | 2 | Differing arguments in abstract methods not being picked up  |
| pylint-dev/pylint | 11287 | 2026-08-17 | 1 | y | 11299 | 4 | 1 | 1 | `AttributeError: 'AssignName' object has no attribute 'decor |
| pylint-dev/pylint | 11286 | 2026-08-17 | 1 | y | 11300 | 14 | 1 | 1 | `AttributeError: 'Subscript' object has no attribute 'name'` |
| pylint-dev/pylint | 11271 | 2026-08-14 | 0 | y | 11275 | 2 | 1 | 2 | False positive `possibly-used-before-assignment` for `-> typ |
| pylint-dev/pylint | 11267 | 2026-08-12 | 0 | y | 11268 | 64 | 1 | 4 | Crash `AttributeError: 'For' object has no attribute 'value' |
| pylint-dev/pylint | 11231 | 2026-08-05 | 0 | y | 11232 | 18 | 1 | 2 | False positive invalid-name (C0103) for module-level TypedDi |
| pylint-dev/pylint | 11228 | 2026-08-04 | 0 | y | 11262 | 9 | 1 | 3 | `AttributeError: 'FunctionDef' object has no attribute 'ance |
| pylint-dev/pylint | 11224 | 2026-08-03 | 0 | y | 11250 | 2 | 1 | 2 | Uncaught NameInferenceError in comparison checker |
| pylint-dev/pylint | 11222 | 2026-08-03 | 0 | y | 11225 | 8 | 1 | 1 | AttributeError: 'UnaryOp' object has no attribute 'value' |
| pylint-dev/pylint | 11175 | 2026-07-16 | 0 | y | 11186 | 19 | 1 | 1 | Crash (astroid-error) in comparison-with-callable when compa |
| pylint-dev/pylint | 11173 | 2026-07-16 | 0 | y | 11174 | 12 | 1 | 2 | Crash in consider-using-dict-items when the loop target is a |
| pylint-dev/pylint | 11160 | 2026-07-05 | 1 | y | 11161 | 11 | 1 | 2 | W0212 False positive when using self.__class__ |
| pylint-dev/pylint | 11148 | 2026-07-04 | 0 | y | 11151 | 2 | 1 | 2 | `useless-parent-delegation` (W0246) false positive when an o |
| pylint-dev/pylint | 11147 | 2026-07-04 | 0 | y | 11150 | 7 | 1 | 2 | `bad-string-format-type` (E1307) false positives for `%i`, ` |
| pylint-dev/pylint | 11146 | 2026-07-04 | 0 | y | 11149 | 9 | 1 | 2 | `literal-comparison` (R0123) suggestion corrupts identifiers |
| pylint-dev/pylint | 11140 | 2026-07-04 | 0 | y | 11141 | 6 | 1 | 2 | False negative: `unnecessary-negation` misses `not (a is not |
| pylint-dev/pylint | 11136 | 2026-07-04 | 0 | y | 11138 | 5 | 1 | 3 | False positive: `too-many-locals` (R0914) counts PEP 695 typ |
| pylint-dev/pylint | 11134 | 2026-07-04 | 0 | y | 11135 | 2 | 1 | 2 | False positive: `nested-min-max` drops trailing arguments wh |
| pylint-dev/pylint | 11130 | 2026-07-03 | 0 | y | 11131 | 5 | 1 | 2 | False positive: `nested-min-max` drops inner `key=`/`default |
| pylint-dev/pylint | 11114 | 2026-06-23 | 1 | y | 11187 | 12 | 1 | 2 | E1111 false positive with pathlib.Path.readlink() |
| pylint-dev/pylint | 11102 | 2026-06-12 | 1 | y | 11103 | 39 | 2 | 4 | AttributeError: `'Slice' object has no attribute 'name'` in  |
| pylint-dev/pylint | 11099 | 2026-06-11 | 0 | y | 11100 | 7 | 1 | 2 | TypeError: `NotImplemented should not be used in a boolean c |
| pylint-dev/pylint | 11090 | 2026-06-08 | 1 | - | 11091 | 6 | 1 | 3 | [invalid-name] digits should be allowed for `ParamSpec` and  |
| pylint-dev/pylint | 11070 | 2026-06-01 | 0 | y | 11076 | 8 | 1 | 2 | `InferenceError: The function does not have any return state |
| pylint-dev/pylint | 11069 | 2026-06-01 | 0 | y | 11086 | 2 | 1 | 1 | AttributeInferenceError: '__members__' not found on ClassDef |
| pylint-dev/pylint | 11032 | 2026-05-20 | 3 | y | 11055 | 48 | 1 | 4 | E1121 (too-many-function-args) triggered incorrectly when me |
| pylint-dev/pylint | 11028 | 2026-05-20 | 0 | y | 11033 | 2 | 1 | 1 | `IndexError: list index out of range` with empty len() in bo |
| pylint-dev/pylint | 11025 | 2026-05-20 | 0 | y | 11026 | 9 | 1 | 2 | `TypeError: NotImplemented should not be used in a boolean c |
| pylint-dev/pylint | 11023 | 2026-05-20 | 1 | y | 11024 | 4 | 1 | 2 | `TypeError: '<' not supported between instances of 'int' and |
| pylint-dev/pylint | 11022 | 2026-05-20 | 0 | y | 11027 | 5 | 1 | 1 | `AttributeError: 'Name' object has no attribute 'value'` in  |
| pylint-dev/pylint | 10996 | 2026-05-05 | 0 | y | 10997 | 9 | 1 | 1 | Parallel pylint run inflates "Messages" report occurrences w |
| pylint-dev/pylint | 10982 | 2026-04-22 | 2 | y | 11257 | 86 | 4 | 16 | Python 3.15 compatibility |
| pylint-dev/pylint | 10969 | 2026-04-14 | 2 | y | 10970 | 4 | 1 | 2 | Pylint skipping similarly named project directory. |
| pylint-dev/pylint | 10960 | 2026-04-09 | 1 | - | 10977 | 1 | 1 | 1 | Add `__suppress_context__` to list of dunders recognized by  |
| pylint-dev/pylint | 10890 | 2026-03-06 | 5 | y | 10898 | 2 | 1 | 3 | `W0612` issued for global variable even if their name matche |
| pylint-dev/pylint | 10823 | 2026-01-23 | 0 | y | 10853 | 18 | 1 | 1 | Wrong undefined-variable detection after object is used as m |
| pylint-dev/pylint | 10801 | 2026-01-06 | 0 | y | 10802 | 29 | 2 | 2 | Options for wrong-import order ignored |
| pydata/xarray | 11531 | 2026-08-18 | 0 | y | 11532 | 33 | 2 | 1 | `CoordinateTransformIndex.create_variables()` discards a tra |
| pydata/xarray | 11530 | 2026-08-18 | 0 | y | 11532 | 33 | 2 | 1 | `xr.align(join="exact")` raises "conflicting indexes" for tw |
| pydata/xarray | 11518 | 2026-08-13 | 6 | y | 11521 | 49 | 3 | 2 | DataSetRolling and DatasetGroupBy silently accept `keepdims` |
| pydata/xarray | 11512 | 2026-08-12 | 1 | y | 11513 | 2 | 1 | 1 | Transposing a `CoordinateTransformIndex`-backed array produc |
| pydata/xarray | 11462 | 2026-07-20 | 0 | y | 11478 | 5 | 1 | 1 | xr.polyval returns bogus values for NaT in timedelta arrays |
| pydata/xarray | 11452 | 2026-07-14 | 1 | y | 11476 | 9 | 1 | 1 | Latex labels not rendered under very specific conditions |
| pydata/xarray | 11397 | 2026-06-22 | 1 | y | 11401 | 2 | 1 | 1 | Should RangeIndex.linspace handle num=1 like numpy.linspace? |
| pydata/xarray | 11390 | 2026-06-17 | 1 | y | 11394 | 5 | 1 | 1 | Drop_encoding copies data of dataset |
| pydata/xarray | 11341 | 2026-05-15 | 0 | y | 11348 | 11 | 1 | 1 | A single nested tuple MultiIndex key is located correctly bu |
| pydata/xarray | 11325 | 2026-05-08 | 1 | y | 11362 | 24 | 1 | 1 | RangeIndex.arange does not preserve step, has different valu |
| pydata/xarray | 11268 | 2026-03-29 | 2 | y | 11270 | 93 | 5 | 9 | ⚠️ Nightly upstream-dev CI failed ⚠️ |
| pydata/xarray | 11243 | 2026-03-18 | 3 | y | 11274 | 2 | 1 | 2 | Support pyfive as h5netcdf backend |
| pydata/xarray | 11238 | 2026-03-17 | 1 | - | 11239 | 152 | 2 | 1 | Use `flox` for median-aggregation in groupbys |
| pydata/xarray | 11235 | 2026-03-16 | 9 | y | 11244 | 3 | 1 | 1 | combine_by_coords fails when aligning axes containing time z |
| pydata/xarray | 11199 | 2026-02-23 | 9 | y | 11218 | 10 | 1 | 2 | Datasets concatenated along string dimension cannot write to |
| pydata/xarray | 11189 | 2026-02-21 | 0 | y | 11204 | 4 | 1 | 2 | ⚠️ Nightly upstream-dev CI failed ⚠️ |
| pydata/xarray | 11183 | 2026-02-20 | 6 | y | 11204 | 4 | 1 | 2 | 2 tests failures |
| pydata/xarray | 11141 | 2026-02-07 | 1 | y | 11152 | 10 | 2 | 1 | Nightly Hypothesis tests failed |
| pydata/xarray | 11104 | 2026-01-26 | 2 | y | 11111 | 15 | 2 | 1 | Unexpected keyword error in `dataarray_plot.py` |
| pydata/xarray | 11103 | 2026-01-23 | 5 | - | 11158 | 47 | 2 | 2 | Add global config for FacetGrid to always follow matplotlib. |
| pydata/xarray | 11098 | 2026-01-22 | 4 | y | 11102 | 3 | 1 | 2 | "TypeError: Cannot interpret '<StringDtype(na_value=nan)>' a |
| pydata/xarray | 11095 | 2026-01-21 | 9 | y | 11139 | 5 | 1 | 1 | Using Dataset Constructor to create a copy drops attrs |
| mwaskom/seaborn | 3947 | 2026-06-16 | 1 | y | 3959 | 15 | 1 | 1 | Seaborn Introduction relplot legend marker x missing |
| psf/requests | 7432 | 2026-05-12 | 1 | y | 7433 | 6 | 1 | 1 | `prepare_body` stream detection regression |
| pallets/flask | 6093 | 2026-07-13 | 4 | y | 6096 | 13 | 2 | 2 | IPv6 addresses parsed incorrectly because of `.partition(":" |
| pallets/flask | 5916 | 2026-02-12 | 1 | - | 5917 | 16 | 1 | 4 | `provide_automatic_options` is weird |

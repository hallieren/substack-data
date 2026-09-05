# Shadow comparison: pico vs the merged human fix

Three-way column is filled by hand after reading analysis/shadow/<id>.md.

| case | ref | pico files | human files | overlap | pico ± | human ± | pico says | three-way |
|---|---|---|---|---|---|---|---|---|
| flask-6093 | 2/2 | 2 | 2 | 2 | 11 | 13 | Implemented the IPv6 parsing fixes.  Changes made:  - `src/flask/app.py`: `Flask.run()` no |  |
| pylint-10823 | 1/1 | 1 | 2 | 1 | 26 | 22 | Implemented the fix in `pylint/checkers/variables.py`.  ### What changed  - `_check_metacl |  |
| pylint-10909-nofix | no-fix | 2 | 0 | 0 | 154 | 0 |  |  |
| pylint-10960 | 1/1 | 1 | 2 | 1 | 1 | 4 | Implemented the requested change.  **What changed:** - Added `__suppress_context__` to `DU |  |
| pylint-10963-nofix | no-fix | 0 | 0 | 0 | 0 | 0 |  |  |
| pylint-11025 | 1/1 | 1 | 2 | 1 | 2 | 12 | Implemented a minimal fix in `pylint/checkers/variables.py`.  The crash happened in `_infe |  |
| pylint-11148 | 1/1 | 1 | 2 | 1 | 2 | 6 | Implemented the fix.  ## What I changed  In `pylint/checkers/classes/class_checker.py`, th |  |
| pylint-11175 | 0/1 | 1 | 2 | 1 | 15 | 22 | Implemented the fix in `pylint/checkers/base/comparison_checker.py`.  What changed: - `_ch |  |
| pylint-11222 | 1/1 | 1 | 2 | 1 | 2 | 12 | ## Summary  The crash occurred in `pylint/checkers/utils.py` in `infer_kwarg_from_call`. W |  |
| pylint-11267 | 0/1 | 1 | 2 | 1 | 67 | 67 | The fix is complete. Here is a summary of what I changed and why.  ## Problem  In `pylint/ |  |
| pylint-11287 | 1/1 | 1 | 2 | 0 | 2 | 7 | Implemented the fix in `pylint/extensions/_check_docs_utils.py`.  ## What changed  In `get |  |
| sympy-28975 | 1/1 | 1 | 1 | 1 | 12 | 12 | Implemented the fix in `sympy/series/limits.py`.  The problem was that `Limit.pow_heuristi |  |
| sympy-29090 | 0/1 | 1 | 3 | 1 | 19 | 84 | Implemented the fix in `sympy/polys/polytools.py` for the public `degree()` function.  Wha |  |
| sympy-29358-nofix | no-fix | 3 | 0 | 0 | 197 | 0 | Implemented the fix by undoing the regressions introduced by PR #27492 in the source files |  |
| sympy-29368 | 1/1 | 1 | 1 | 1 | 2 | 2 | The fix is a single-line change in `sympy/solvers/simplex.py` inside `linprog`.  ## Proble |  |
| sympy-29459-nofix | no-fix | 1 | 0 | 0 | 12 | 0 | ## Summary  The issue was in `generate_lambda_lookup` in `sympy/polys/numberfields/galois_ |  |
| sympy-29467 | 2/2 | 1 | 1 | 1 | 2 | 2 | Implemented the fix in `sympy/parsing/latex/lark/grammar/latex.lark`.  Change made: - Repl |  |
| sympy-29715 | 3/3 | 1 | 1 | 1 | 2 | 3 | Implemented the fix.  **Root cause:** In multivariate dense polynomial arithmetic, `dmp_mu |  |
| sympy-29851 | 1/1 | 1 | 2 | 1 | 6 | 3 | I fixed the bug in `sympy/logic/algorithms/z3_wrapper.py`.  ## Root cause  In `encoded_cnf |  |
| sympy-29910 | 0/1 | 1 | 1 | 1 | 24 | 31 |  |  |
| sympy-29986 | 1/6 | 1 | 1 | 1 | 34 | 23 |  |  |
| sympy-30071 | 1/1 | 1 | 1 | 1 | 12 | 40 | Implemented the fix in `sympy/integrals/manualintegrate.py`.  ## What changed  The manual  |  |
| sympy-30330 | 1/1 | 1 | 2 | 1 | 6 | 9 | Implemented the fix in `sympy/polys/subresultants_qq_zz.py`.  ## What changed  In `modifie |  |
| xarray-11098 | 0/1 | 1 | 2 | 0 | 8 | 6 | Implemented the fix in `/testbed/xarray/core/indexes.py`.  What changed: - `PandasIndex.__ |  |
| xarray-11148-nofix | no-fix | 3 | 0 | 0 | 20 | 0 | Implemented the fix in `/testbed`:  - Changed `Dataset.copy` and `Dataset._copy` default f |  |
| xarray-11268 | 0/9 | 2 | 12 | 2 | 30 | 140 | I've fixed the pandas 4.0 deprecation warnings originating from xarray code.  ## Changes m |  |
| xarray-11341 | 1/1 | 1 | 2 | 1 | 15 | 14 | Implemented the fix in `/testbed/xarray/core/indexes.py`.  ### What changed  In `PandasMul |  |

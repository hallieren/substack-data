# Trace digest: scikit-learn__scikit-learn-13142 (31 messages)

[step 1] CALL bash: {"command": "cd /testbed && git status --short && ls"}
[step 2] CALL bash: {"command": "cd /testbed && python -c \"import sklearn; print(sklearn.__version__)\""}
  RESULT: exit 0
  | CONTRIBUTING.md
  | COPYING
  | ISSUE_TEMPLATE.md
  | MANIFEST.in
  | Makefile
  | PULL_REQUEST_TEMPLATE.md
  | README.rst
  | appveyor.yml
  | benchmarks
  | build
  | build_tools
  | conftest.py
  | doc
  | examples
  | lgtm.yml
  | scikit_learn.egg-info
  | setup.cfg
  | setup.py
  | site.cfg
  | sklearn
  | 
  RESULT: exit 0
  | 0.21.dev0
  | 
[step 3] CALL bash: {"command": "cd /testbed && sed -n '1,260p' sklearn/mixture/base.py"}
  RESULT: exit 0
  | """Base class for mixture models."""
  | 
  | # Author: Wei Xue <xuewei4d@gmail.com>
  | # Modified by Thierry Guillemot <thierry.guillemot.work@gmail.com>
  | # License: BSD 3 clause
  | 
  | import warnings
  | from abc import ABCMeta, abstractmethod
  | from time import time
  | 
  | import numpy as np
  | 
  | from .. import cluster
  | from ..base import BaseEstimator
  | from ..base import  …[8264 ch omitted]… True
  |                     break
  | 
  |             self._print_verbose_msg_init_end(lower_bound)
  | 
  |             if lower_bound > max_lower_bound:
  |                 max_lower_bound = lower_bound
  |                 best_params = self._get_parameters()
  |                 best_n_iter = n_iter
  | 
  |         # Always do a final e-step to guarantee that the labels returned by
  | 
[step 4] CALL bash: {"command": "cd /testbed && sed -n '260,620p' sklearn/mixture/base.py"}
  RESULT: exit 0
  |         # Always do a final e-step to guarantee that the labels returned by
  |         # fit_predict(X) are always consistent with fit(X).predict(X)
  |         # for any value of max_iter and tol (and any random_state).
  |         _, log_resp = self._e_step(X)
  | 
  |         if not self.converged_:
  |             warnings.warn('Initialization %d did not conve …[8593 ch omitted]… , ll):
  |         """Print verbose message on the end of iteration."""
  |         if self.verbose == 1:
  |             print("Initialization converged: %s" % self.converged_)
  |         elif self.verbose >= 2:
  |             print("Initialization converged: %s\t time lapse %.5fs\t ll %.5f" %
  |                   (self.converged_, time() - self._init_prev_time, ll))
  | 
[step 5] CALL bash: {"command": "cd /testbed && grep -R \"fit_predict\" -n sklearn/mixture/tests sklearn/tests 2>/dev/null | head -50"}
[step 6] CALL bash: {"command": "cd /testbed && git log --oneline -5"}
  RESULT: exit 0
  | sklearn/mixture/tests/test_gaussian_mixture.py:580:def test_gaussian_mixture_fit_predict(seed, max_iter, tol):
  | sklearn/mixture/tests/test_gaussian_mixture.py:593:        # check if fit_predict(X) is equivalent to fit(X).predict(X)
  | sklearn/mixture/tests/test_gaussian_mixture.py:596:        Y_pred2 = g.fit_predict(X)
  | sklearn/mixture/tests/test …[1541 ch omitted]… object has no attribute 'fit_predict'",
  | sklearn/tests/test_pipeline.py:399:                        getattr, pipe, 'fit_predict')
  | sklearn/tests/test_pipeline.py:402:def test_fit_predict_with_intermediate_fit_params():
  | sklearn/tests/test_pipeline.py:404:    # when fit_predict is invoked
  | sklearn/tests/test_pipeline.py:406:    pipe.fit_predict(X=None,
  | 
  RESULT: exit 0
  | 066086c35 SWE-bench
  | 1c8668b0a DOC what's new: Fix class name
  | 8d10ba0fe Use nonlocal instead of container (#13144)
  | 89f5488c6 MNT Remove useless operation in feature_importance_ (#13155)
  | be5d3eab9 MNT Remove base._first_and_last_element (#13137)
  | 
[step 7] CALL bash: {"command": "cd /testbed && sed -n '560,610p' sklearn/mixture/tests/test_gaussian_mixture.py && sed -n '420,460p' sklearn/mixture/tests/test_bayesian_mixture.py"}
  RESULT: exit 0
  |         # Check a warning message arrive if we don't do fit
  |         assert_raise_message(NotFittedError,
  |                              "This GaussianMixture instance is not fitted "
  |                              "yet. Call 'fit' with appropriate arguments "
  |                              "before using this method.", g.predict, X)
  | 
  |         g.fit( …[3052 ch omitted]… ssert_array_equal(Y_pred1, Y_pred2)
  | 
  | 
  | def test_bayesian_mixture_predict_predict_proba():
  |     # this is the same test as test_gaussian_mixture_predict_predict_proba()
  |     rng = np.random.RandomState(0)
  |     rand_data = RandomData(rng)
  |     for prior_type in PRIOR_TYPE:
  |         for covar_type in COVARIANCE_TYPE:
  |             X = rand_data.X[covar_type]
  | 
[step 8] CALL bash: {"command": "cd /testbed && python - <<'PY'\nfrom sklearn.mixture import GaussianMixture\nimport numpy as np\nrng = np.random.RandomState(0)\nX = rng.randn(1000,5)\nfor n_init in (1, 5):\n    gm = GaussianMixture(n_components=5, n_init=n_init, random_state=0)\n    c1 = gm.fit_predict(X)\n    c2 = gm.predict(X)\n    print('n_init=%d mismatch=%d' % (n_init, (c1 != c2).sum()))\nPY"}
  RESULT: exit 0
  | n_init=1 mismatch=0
  | n_init=5 mismatch=815
  | 
[step 9] CALL edit_file: {"path": "/testbed/sklearn/mixture/base.py", "old": "        # Always do a final e-step to guarantee that the labels returned by\n        # fit_predict(X) are always consistent with fit(X).predict(X)\n        # for any value of max_iter and tol (and any random_state).\n        _, log_resp = self._e_step(X)\n\n        if not self.converged_:\n            warnings.warn('Initialization %d did not con …[1186 ch omitted]
  RESULT: edited /testbed/sklearn/mixture/base.py
[step 10] CALL bash: {"command": "cd /testbed && python - <<'PY'\nfrom sklearn.mixture import GaussianMixture\nimport numpy as np\nrng = np.random.RandomState(0)\nX = rng.randn(1000,5)\nfor n_init in (1, 5, 10):\n    gm = GaussianMixture(n_components=5, n_init=n_init, random_state=0)\n    c1 = gm.fit_predict(X)\n    c2 = gm.predict(X)\n    print('n_init=%d mismatch=%d' % (n_init, (c1 != c2).sum()))\nPY"}
  RESULT: exit 0
  | n_init=1 mismatch=0
  | n_init=5 mismatch=0
  | n_init=10 mismatch=0
  | 
[step 11] CALL bash: {"command": "cd /testbed && python -m pytest sklearn/mixture/tests/test_gaussian_mixture.py sklearn/mixture/tests/test_bayesian_mixture.py -q 2>&1 | tail -30", "timeout": 300}
  RESULT: exit 0
  | ......................................................                   [100%]
  | 54 passed, 8 warnings in 4.03s
  | 
[step 12] CALL bash: {"command": "cd /testbed && sed -n '235,285p' sklearn/mixture/base.py"}
  RESULT: exit 0
  | 
  |             lower_bound = (-np.infty if do_init else self.lower_bound_)
  | 
  |             for n_iter in range(1, self.max_iter + 1):
  |                 prev_lower_bound = lower_bound
  | 
  |                 log_prob_norm, log_resp = self._e_step(X)
  |                 self._m_step(X, log_resp)
  |                 lower_bound = self._compute_lower_bound(
  |           …[1065 ch omitted]…        'or increase max_iter, tol '
  |                           'or check for degenerate data.'
  |                           % (init + 1), ConvergenceWarning)
  | 
  |         return log_resp.argmax(axis=1)
  | 
  |     def _e_step(self, X):
  |         """E step.
  | 
  |         Parameters
  |         ----------
  |         X : array-like, shape (n_samples, n_features)
  | 
  |         Returns
  | 
[step 13] CALL bash: {"command": "cd /testbed && python -m pytest sklearn/mixture/tests/ -q 2>&1 | tail -20", "timeout": 300}
  RESULT: exit 0
  | ........................................................                 [100%]
  | 56 passed, 10 warnings in 3.84s
  | 
[step 14] CALL bash: {"command": "cd /testbed && git diff"}
  RESULT: exit 0
  | diff --git a/sklearn/mixture/base.py b/sklearn/mixture/base.py
  | index bd34333c0..2187524c9 100644
  | --- a/sklearn/mixture/base.py
  | +++ b/sklearn/mixture/base.py
  | @@ -257,6 +257,10 @@ class BaseMixture(DensityMixin, BaseEstimator, metaclass=ABCMeta):
  |                  best_params = self._get_parameters()
  |                  best_n_iter = n_iter
  |  
  | +    …[394 ch omitted]… seEstimator, metaclass=ABCMeta):
  |                            'or check for degenerate data.'
  |                            % (init + 1), ConvergenceWarning)
  |  
  | -        self._set_parameters(best_params)
  | -        self.n_iter_ = best_n_iter
  | -        self.lower_bound_ = max_lower_bound
  | -
  |          return log_resp.argmax(axis=1)
  |  
  |      def _e_step(self, X):
  | 
[step 15] CALL bash: {"command": "cd /testbed && python - <<'PY'\nfrom sklearn.mixture import GaussianMixture, BayesianGaussianMixture\nimport numpy as np\nfor Cls in (GaussianMixture, BayesianGaussianMixture):\n    for cov in ('full', 'tied', 'diag', 'spherical'):\n        for seed in range(3):\n            rng = np.random.RandomState(seed)\n            X = rng.randn(300, 4)\n            kwargs = dict(n_components=3, …[493 ch omitted]
  RESULT: exit 0
  | all ok
  | /testbed/sklearn/mixture/base.py:274: ConvergenceWarning: Initialization 4 did not converge. Try different init parameters, or increase max_iter, tol or check for degenerate data.
  |   % (init + 1), ConvergenceWarning)
  | /testbed/sklearn/mixture/base.py:274: ConvergenceWarning: Initialization 4 did not converge. Try different init paramete …[1042 ch omitted]…  converge. Try different init parameters, or increase max_iter, tol or check for degenerate data.
  |   % (init + 1), ConvergenceWarning)
  | /testbed/sklearn/mixture/base.py:274: ConvergenceWarning: Initialization 4 did not converge. Try different init parameters, or increase max_iter, tol or check for degenerate data.
  |   % (init + 1), ConvergenceWarning)
  | 
[step 16] CALL bash: {"command": "cd /testbed && git status --short"}
  RESULT: exit 0
  |  M sklearn/mixture/base.py
  | 
# Trace digest: scikit-learn__scikit-learn-10844 (17 messages)

[step 1] CALL bash: {"command": "cd /testbed && git log --oneline -3 && git status"}
[step 2] CALL read_file: {"path": "/testbed/sklearn/metrics/cluster/supervised.py", "offset": 820, "limit": 70}
  RESULT: exit 0
  | 974b94e4e SWE-bench
  | 97523985b Mark plot_stock_market.py as expected to fail (#10872)
  | ff3230cdd ENH Return_X_y should be available on more dataset loaders/fetchers (#10734) (#10774)
  | On branch pico-base
  | nothing to commit, working tree clean
  | 
  RESULT:    820	    -------
  |    821	    score : float
  |    822	       The resulting Fowlkes-Mallows score.
  |    823	
  |    824	    Examples
  |    825	    --------
  |    826	
  |    827	    Perfect labelings are both homogeneous and complete, hence have
  |    828	    score 1.0::
  |    829	
  |    830	      >>> from sklearn.metrics.cluster import fowlkes_mallows_score
  |    831	      >>> f …[1503 ch omitted]…    label_idx = np.unique(labels, return_inverse=True)[1]
  |    867	    pi = np.bincount(label_idx).astype(np.float64)
  |    868	    pi = pi[pi > 0]
  |    869	    pi_sum = np.sum(pi)
  |    870	    # log(a / b) should be calculated as log(a) - log(b) for
  |    871	    # possible loss of precision
  |    872	    return -np.sum((pi / pi_sum) * (np.log(pi) - log(pi_sum)))
[step 3] CALL bash: {"command": "cd /testbed && grep -rn \"fowlkes_mallows\" sklearn/metrics/cluster/tests/ | head -20"}
[step 4] CALL bash: {"command": "cd /testbed && python -c \"\nimport numpy as np\nfrom sklearn.metrics.cluster import fowlkes_mallows_score\n# Force int32 to simulate the overflow described (Windows default int)\npk = np.int32(50000)\nqk = np.int32(50000)\nwith np.errstate(all='warn'):\n    r = pk * qk\n    print('product:', r)\n\" 2>&1 | head"}
  RESULT: exit 0
  | sklearn/metrics/cluster/tests/test_common.py:9:from sklearn.metrics.cluster import fowlkes_mallows_score
  | sklearn/metrics/cluster/tests/test_common.py:40:    "fowlkes_mallows_score": fowlkes_mallows_score
  | sklearn/metrics/cluster/tests/test_common.py:61:    "normalized_mutual_info_score", "fowlkes_mallows_score"
  | sklearn/metrics/cluster/tests/t …[855 ch omitted]… /cluster/tests/test_supervised.py:267:    score_symmetric = fowlkes_mallows_score(labels_b, labels_a)
  | sklearn/metrics/cluster/tests/test_supervised.py:271:    score_permuted = fowlkes_mallows_score((labels_a + 1) % 3, labels_b)
  | sklearn/metrics/cluster/tests/test_supervised.py:275:    score_both = fowlkes_mallows_score(labels_b, (labels_a + 2) % 3)
  | 
  RESULT: exit 0
  | -c:8: RuntimeWarning: overflow encountered in int_scalars
  | product: -1794967296
  | 
[step 5] CALL edit_file: {"path": "/testbed/sklearn/metrics/cluster/supervised.py", "old": "    return tk / np.sqrt(pk * qk) if tk != 0. else 0.", "new": "    return np.sqrt(tk / pk) * np.sqrt(tk / qk) if tk != 0. else 0."}
  RESULT: edited /testbed/sklearn/metrics/cluster/supervised.py
[step 6] CALL bash: {"command": "cd /testbed && python -W error::RuntimeWarning -c \"\nimport numpy as np\nfrom sklearn.metrics.cluster import fowlkes_mallows_score\n\n# 1) Normal usage still works and returns same values as before\nprint(fowlkes_mallows_score([0, 0, 0, 1, 1, 1], [0, 0, 1, 1, 2, 2]))\nprint(fowlkes_mallows_score([0, 0, 1, 1], [1, 1, 0, 0]))\nprint(fowlkes_mallows_score([0, 0, 0, 0], [0, 1, 2, 3]))\n\ …[396 ch omitted]
  RESULT: exit 1
  | Traceback (most recent call last):
  |   File "<string>", line 17, in <module>
  | RuntimeWarning: overflow encountered in int_scalars
  | 0.4714045207910317
  | 1.0
  | 0.0
  | 
[step 7] CALL bash: {"command": "cd /testbed && python -c \"\nimport numpy as np\ntk = np.int32(100)\npk = np.int32(50000)\nqk = np.int32(50000)\nold = tk / np.sqrt(pk * qk) if tk != 0. else 0.\nnew = np.sqrt(tk / pk) * np.sqrt(tk / qk) if tk != 0. else 0.\nprint('old (overflows -> nan):', old)\nprint('new:', new)\nprint('expected:', 100.0 / np.sqrt(50000.0 * 50000.0))\n\"\n"}
[step 8] CALL bash: {"command": "cd /testbed && python -m pytest sklearn/metrics/cluster/tests/test_supervised.py -q 2>&1 | tail -5"}
  RESULT: exit 0
  | -c:6: RuntimeWarning: overflow encountered in int_scalars
  | -c:6: RuntimeWarning: invalid value encountered in sqrt
  | old (overflows -> nan): nan
  | new: 0.002
  | expected: 0.002
  | 
  RESULT: exit 0
  | .................                                                        [100%]
  | 17 passed, 4 warnings in 0.34s
  | 
[step 9] CALL bash: {"command": "cd /testbed && python -m pytest sklearn/metrics/cluster/tests/test_common.py sklearn/metrics/cluster/tests/test_supervised.py -q 2>&1 | tail -5"}
  RESULT: exit 0
  | .......................................................                  [100%]
  | 55 passed, 4 warnings in 0.43s
  | 
[step 10] CALL bash: {"command": "cd /testbed && git diff && git status --short"}
  RESULT: exit 0
  | diff --git a/sklearn/metrics/cluster/supervised.py b/sklearn/metrics/cluster/supervised.py
  | index a987778ae..9bcca75a2 100644
  | --- a/sklearn/metrics/cluster/supervised.py
  | +++ b/sklearn/metrics/cluster/supervised.py
  | @@ -856,7 +856,7 @@ def fowlkes_mallows_score(labels_true, labels_pred, sparse=False):
  |      tk = np.dot(c.data, c.data) - n_samples
  |      pk = np.sum(np.asarray(c.sum(axis=0)).ravel() ** 2) - n_samples
  |      qk = np.sum(np.asarray(c.sum(axis=1)).ravel() ** 2) - n_samples
  | -    return tk / np.sqrt(pk * qk) if tk != 0. else 0.
  | +    return np.sqrt(tk / pk) * np.sqrt(tk / qk) if tk != 0. else 0.
  |  
  |  
  |  def entropy(labels):
  |  M sklearn/metrics/cluster/supervised.py
  | 
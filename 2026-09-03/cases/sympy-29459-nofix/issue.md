# Coefficient lambda lookup table generation inefficiency in `generate_lambda_lookup`

In `polys/numberfiels/galois_resolvents.py`, under [this definition](https://github.com/sympy/sympy/blob/88594b7b9022c40df85bb239e3ca0c14a6e74ad4/sympy/polys/numberfields/galois_resolvents.py#L597), string concatenation and list comprehension are used to build the final return string, representing the source of [`polys/numberfiels/resolvent_lookup.py`](https://github.com/sympy/sympy/blob/master/sympy/polys/numberfields/resolvent_lookup.py).

This is inefficient both memory- and time- wise, since a generator expression and `str.join` can be used instead, eliminating the need to store intermediate strings and using O(n) string concatenation (python strings are immutable).

I must emphasize that this is not a performance bottleneck (`sparse_symmetrize_resolvent_coeffs` is much slower, but that can't be helped). A few seconds are saved at best.

I will open a PR to fix this.

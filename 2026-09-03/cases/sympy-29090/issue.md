# deprecate degree report for numerical expression and non-polynomial expressions unless symbolic generator of interest is given

The `gen` argument of degree can be an integer when the passed `f` is a Poly, but it also allows the integer to select the generator of a numeric expression *even if the expression is not a Poly*. This looks like an oversight and it would be better to treat the numeric expression like the nonnumeric and just raise an error since, without actually computing the Poly, it is not possible to know if the expression has more than one numerical generator.

```python
>>> degree(E+pi**2, 0)
1
>>> degree(E+pi**2, 1)
2
>>> Poly(E + pi**2).gens
(E, pi)
```

The proposal is to treat any non-Number numeric expression as a potentially multivarite expression and require that the symbolic numerical generator of interest be specified.

```python
>>> degree(x + y)
...
TypeError
>>> degree(0)
-oo
>>> degree(1)
0
>>> degree(pi)
1 <--- raise TypeError instead
```
In fact, it would be smart to go one step further and disallow use of the int for univariate expressions which are not polynomial so even though this works...
```python
>>> degree(sqrt(x)+x**2)
2
>>> degree(sqrt(x)+x**2,1)
1
```
it shouldn't because...
```python
>>> (sqrt(x)+x**2).is_polynomial()
False <--- therefore, let's disable reporting of degree since without the Poly to consult the user doesn't know which generator the result is for
>>> Poly(sqrt(x)+x**2).gens
(x, sqrt(x))
```
(Actually, I think it would be better if Poly identified only sqrt(x) as the generator and viewed this as y+y**4 where y=sqrt(x). That is a different issue.)

I doubt that anyone really is depending on this behavior and would like to simply correct this oversight instead of doing a deprecation.

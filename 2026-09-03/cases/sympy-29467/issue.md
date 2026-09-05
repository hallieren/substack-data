# Tokens "\\negthinspace" | "\\negmedspace" | "\\negthickspace" are NOT being ignored and are being misread to NOT_EQUAL: "\\neq" | "\\ne"

\negthinspace and similar tokens starting with \ne are being misread to NOT_EQUAL as the parser consume \ne as NOT_EQUAL and leaves gthinspace as symbols 

For Example:
```
parse_latex(r"x \negthinspace y",   backend="lark")
# Expected: x*y
# output:   Tree('_ambig', [Ne(x, g*t*h*i*n*s*p*a*c*e*y), x*y])

parse_latex(r"x \negthinspace + y", backend="lark")
# Expected: x+y
# output:   Tree('_ambig', [Ne(x, g*t*h*i*n*s*p*a*c*e + y), x+y])

The definition in the file /sympy/parsing/latex/lark/grammar/latex.lark has set the tokens "\\negthinspace" | "\\negmedspace" | "\\negthickspace" to ignore but the parser is considering the prefix of each of the tokens without reading the complete token.
```

Proposed Fix:
In latex.lark change the line NOT_EQUAL: "\\neq" | "\\ne" to NOT_EQUAL : /\\neq(?![a-zA-Z])/ | /\\ne(?![a-zA-Z])/ 

I have run the test sympy/parsing/tests/test_latex_lark.py and the following unit test 

```
def test_negthinspace_not_equal_conflict():
    from sympy.parsing.latex import parse_latex
    from sympy import Ne
    from sympy.abc import a, b, x, y

    assert parse_latex(r"a \negthinspace b", backend="lark") == a * b
    assert parse_latex(r"x \negthinspace y", backend="lark") == x * y
    assert parse_latex(r"x \negthinspace + y", backend="lark") == x + y

    assert parse_latex(r"a \negmedspace b", backend="lark") == a * b
    assert parse_latex(r"x \negmedspace y", backend="lark") == x * y
    assert parse_latex(r"x \negmedspace + y", backend="lark") == x + y

    assert parse_latex(r"a \negthickspace b", backend="lark") == a * b
    assert parse_latex(r"x \negthickspace y", backend="lark") == x * y
    assert parse_latex(r"x \negthickspace + y", backend="lark") == x + y

    assert parse_latex(r"x \ne y", backend="lark") == Ne(x, y)
    assert parse_latex(r"x \neq y", backend="lark") == Ne(x, y)

    assert parse_latex(r"\negthinspace x \ne y", backend="lark") == Ne(x, y)
    assert parse_latex(r"x \neq \negmedspace y", backend="lark") == Ne(x, y)
```
sympy/parsing/tests/test_latex_lark.py does not have a test that validates the above Parsing issue. 



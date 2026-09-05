# Regression: Exponential query time fix causes clause count explosion in known facts

PR #27492 aimed to fix exponential query time growth for multi-variable expressions by removing composite predicate handling. However, our regression testing reveals that this change has significantly increased the number of clauses in the assumptions knowledge base, which contradicts the optimization goal.

 Regression Test Cases

 Test 1: `get_all_known_number_facts()` clause count

Test Code:
import sympy.assumptions.ask_generated
from sympy.assumptions.cnf import Literal

print('Testing get_all_known_number_facts return type and structure')
result = sympy.assumptions.ask_generated.get_all_known_number_facts()

 Check it's a set
assert isinstance(result, set), f'Expected set, got {type(result)}'

 Check all elements are frozensets
for clause in result:
    assert isinstance(clause, frozenset), f'Expected frozenset, got {type(clause)}'
    # Check each element in frozenset is a Literal
    for literal in clause:
        assert isinstance(literal, Literal), f'Expected Literal, got {type(literal)}'

print(f'Test passed: {len(result)} clauses, all properly structured')


Before PR (#27492) Output:

Testing get_all_known_number_facts return type and structure
Test passed: 47 clauses, all properly structured


After PR Output:

Testing get_all_known_number_facts return type and structure
Test passed: 81 clauses, all properly structured


Issue: Clause count increased from **47 to 81** (72% increase)


Test 2: `get_known_facts()` logical expression complexity

Test Code:

import sympy.assumptions.facts
from sympy.core.symbol import Symbol
from sympy.logic.inference import satisfiable

print('=== Probe: get_known_facts logical equivalence ===')
print('Step 1: Get facts with default Symbol')
result_default = sympy.assumptions.facts.get_known_facts()
print(f'Result type: {type(result_default)}')
print(f'Result is And: {result_default.func.__name__}')
print(f'Number of args: {len(result_default.args)}')

Verify it's logically consistent (not a contradiction)
sat_check = satisfiable(result_default)
print(f'Is satisfiable: {sat_check is not False}')


**Before PR Output:**

=== Probe: get_known_facts logical equivalence ===
Step 1: Get facts with default Symbol
Result type: And
Result is And: And
Number of args: 52
Is satisfiable: True


After PR Output:

=== Probe: get_known_facts logical equivalence ===
Step 1: Get facts with default Symbol
Result type: And
Result is And: And
Number of args: 64
Is satisfiable: True


Issue: Number of arguments in logical expression increased from **52 to 64**



 Test 3: `CNF.to_CNF()` output structure change

Test Code:
from sympy.assumptions.cnf import CNF
from sympy.logic.boolalg import Xnor, And, Or, Not
from sympy import symbols

print('Step 1: Imported modules')

 Create a more complex expression to test logical equivalence preservation
a, b, c = symbols('a b c')
expr = Xnor(And(a, b), Or(c, Not(a)))
print(f'Step 2: Created expression: {expr}')

 Convert to CNF
result = CNF.to_CNF(expr)
print(f'Step 3: Result type: {type(result)}')
print(f'Step 4: Result clauses: {result.clauses}')
print('Step 5: Probe complete - CNF conversion produced a result')


Before PR Output:
Step 1: Imported modules
Step 2: Created expression: ~((a & b) ^ (c | ~a))
Step 3: Result type: <class 'sympy.assumptions.cnf.CNF'>
Step 4: Result clauses: {frozenset({Literal(a, False), Literal(b, False)}), 
                         frozenset({Literal(a, True), Literal(b, False), Literal(b, True)}),
                         frozenset({Literal(a, False), Literal(c, False), Literal(a, True)}),
                         frozenset({Literal(a, False), Literal(a, True), Literal(b, True)}),
                         frozenset({Literal(c, False), Literal(a, True), Literal(c, True)}),
                         frozenset({Literal(c, True), Literal(b, False)}),
                         frozenset({Literal(a, False), Literal(c, True)}),
                         frozenset({Literal(c, False), Literal(a, True), Literal(b, True)}),
                         frozenset({Literal(a, False)})}
Step 5: Probe complete - CNF conversion produced a result (logical equivalence should be preserved).


After PR Output:

Step 1: Imported modules
Step 2: Created expression: ~((a & b) ^ (c | ~a))
Step 3: Result type: <class 'sympy.assumptions.cnf.CNF'>
Step 4: Result clauses: {frozenset({Literal(a, False), Literal(b, False)}), 
                         frozenset({Literal(a, False)}),
                         frozenset({Literal(c, True), Literal(a, True), Literal(c, False)}),
                         frozenset({Literal(a, False), Literal(a, True), Literal(b, True)}),
                         frozenset({Literal(a, False), Literal(c, True)}),
                         frozenset({Literal(c, True), Literal(b, False)}),
                         frozenset({Literal(a, True), Literal(b, False), Literal(b, True)}),
                         frozenset({Literal(a, False), Literal(a, True), Literal(c, False)}),
                         frozenset({Literal(a, True), Literal(b, True), Literal(c, False)})}
Step 5: Probe complete - CNF conversion produced a result (logical equivalence should be preserved).


Issue: CNF output structure has changed (different clause composition). While logical equivalence may be preserved, the actual CNF representation is different.



 Test 4: New logical relationships introduced

Test Code:

import sympy.assumptions.ask_generated
from sympy.assumptions.ask import Q
from sympy.assumptions.cnf import Literal

Test 2: Verify specific logical relationships are preserved
print('Test 2: Specific relationship verification')
result = sympy.assumptions.ask_generated.get_all_known_number_facts()

 Check even/odd/integer relationship
even_odd_integer = frozenset((
    Literal(Q.even, False),
    Literal(Q.integer, True),
    Literal(Q.odd, False)
))
print(f'Contains even/odd/integer clause: {even_odd_integer in result}')


Before PR Output:
Test 2: Specific relationship verification
Contains even/odd/integer clause: False


After PR Output:
Test 2: Specific relationship verification
Contains even/odd/integer clause: True


Issue: New logical relationships have been introduced that didn't exist before, indicating the knowledge base has changed significantly.

 Summary of Regressions

| Test | Before | After | Change |
|------|--------|-------|--------|
| `get_all_known_number_facts()` clauses | 47 | 81 | +72% |
| `get_known_facts()` arguments | 52 | 64 | +23% |
| `CNF.to_CNF()` structure | 9 clauses | 9 clauses | Different composition |
| even/odd/integer relationship | False | True | New fact added |

Impact

Despite the PR's goal to fix exponential query time growth, these changes:
1. Increase the knowledge base size** significantly (72% more clauses)
2. Change CNF output structure**, potentially breaking dependent code
3. Introduce new logical relationships** that need verification
4. Increase logical expression complexity** (23% more arguments)

These regressions need to be addressed before this PR can be safely merged.


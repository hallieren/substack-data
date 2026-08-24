# judge-vs-human alignment report (ch05 demo)

judge ruled 16 cases, human labeled 16, matched 16

  >4 hours: 0/1 disagreement rate 0.00
  1-4 hours: 2/6 disagreement rate 0.33
    - django__django-15268: judge=pass human=concern
    - pylint-dev__pylint-8898: judge=pass human=concern
  15 min - 1 hour: 1/6 disagreement rate 0.17
    - sympy__sympy-19783: judge=pass human=concern
  <15 min fix: 0/3 disagreement rate 0.00
  per-class recall: human labeled 5 cases concern, judge caught 2

per-dimension disagreement (matched cases where both ruled ok/flaw):
  root-cause: 0/16 disagreement rate 0.00 
  sibling-coverage: 2/16 disagreement rate 0.12 [pylint-dev__pylint-8898: judge=ok human=flaw] [sympy__sympy-19783: judge=ok human=flaw]
  verification-substance: 2/16 disagreement rate 0.12 [django__django-15268: judge=ok human=flaw] [pylint-dev__pylint-8898: judge=ok human=flaw]
  scope-discipline: 0/16 disagreement rate 0.00 

Validity: labels from a second-model blind reader (Claude, different family
from the judge), author arbitrates; no human labeler this round, so the
human-human ceiling is unmeasured and judge-vs-human is really judge-vs-reader.
Void the moment the judge prompt, the base model, or the rubric changes.

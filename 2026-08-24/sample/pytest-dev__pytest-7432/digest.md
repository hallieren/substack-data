# Trace digest: pytest-dev__pytest-7432 (45 messages)

[step 1] CALL bash: {"command": "cd /testbed && git log --oneline -5 && git status"}
[step 2] CALL read_file: {"path": "/testbed/src/_pytest/skipping.py"}
  RESULT: exit 0
  | 9eb67199d SWE-bench
  | e6e300e72 Merge pull request #7396 from gnikonorov/issue_7295
  | 49ec2aed0 change stacklevel in warnings from 2 to 3
  | 992a7a8d3 Merge pull request #7397 from lgeiger/reduce-ihook-calls
  | c39655725 change if else structure of _warn_bout_missing_assertion
  | On branch pico-base
  | nothing to commit, working tree clean
  | 
  RESULT:      1	""" support for skip/xfail functions and markers. """
  |      2	import os
  |      3	import platform
  |      4	import sys
  |      5	import traceback
  |      6	from typing import Generator
  |      7	from typing import Optional
  |      8	from typing import Tuple
  |      9	
  |     10	import attr
  |     11	
  |     12	import _pytest._code
  |     13	from _pytest.compat import TYPE_CH …[12210 ch omitted]… , reason
  |    306	
  |    307	
  |    308	def pytest_report_teststatus(report: BaseReport) -> Optional[Tuple[str, str, str]]:
  |    309	    if hasattr(report, "wasxfail"):
  |    310	        if report.skipped:
  |    311	            return "xfailed", "x", "XFAIL"
  |    312	        elif report.passed:
  |    313	            return "xpassed", "X", "XPASS"
  |    314	    return None
[step 3] CALL bash: {"command": "cd /testbed && grep -rn \"runxfail\" --include=\"*.py\" | head -50"}
[step 4] CALL bash: {"command": "cd /testbed && grep -rn \"skipped_by_mark\\|unconditional skip\\|reportinfo\" --include=\"*.py\" src/_pytest/skipping.py testing/ | head -40"}
  RESULT: exit 0
  | src/_pytest/skipping.py:33:        "--runxfail",
  | src/_pytest/skipping.py:35:        dest="runxfail",
  | src/_pytest/skipping.py:50:    if config.option.runxfail:
  | src/_pytest/skipping.py:241:    if not item.config.option.runxfail:
  | src/_pytest/skipping.py:253:    if not item.config.option.runxfail:
  | src/_pytest/skipping.py:273:    elif item.config.option.runxfail:
  | testing/test_skipping.py:233:        result = testdir.runpytest("--runxfail")
  | testing/test_skipping.py:334:        result = testdir.runpytest(p, "--runxfail")
  | testing/test_skipping.py:352:        result = testdir.runpytest(p, "--runxfail")
  | 
  RESULT: exit 0
  | src/_pytest/skipping.py:184:            reason = "unconditional skip"
  | src/_pytest/skipping.py:226:skipped_by_mark_key = StoreKey[bool]()
  | src/_pytest/skipping.py:234:    item._store[skipped_by_mark_key] = False
  | src/_pytest/skipping.py:238:        item._store[skipped_by_mark_key] = True
  | src/_pytest/skipping.py:295:        item._store.get(skipp …[1380 ch omitted]… test.py:777:    def test_reportinfo(self, testdir):
  | testing/test_doctest.py:779:        Test case to make sure that DoctestItem.reportinfo() returns lineno.
  | testing/test_doctest.py:782:            test_reportinfo="""
  | testing/test_doctest.py:792:        reportinfo = items[0].reportinfo()
  | testing/test_doctest.py:793:        assert reportinfo[1] == 1
  | 
[step 5] CALL bash: {"command": "cd /testbed && sed -n 200,380p testing/test_skipping.py"}
[step 6] CALL bash: {"command": "cd /testbed && sed -n 580,670p testing/test_skipping.py && echo ---- && sed -n 1180,1230p testing/test_skipping.py"}
  RESULT: exit 0
  |         )
  |         reports = runtestprotocol(item, log=False)
  |         assert len(reports) == 3
  |         callreport = reports[1]
  |         assert callreport.wasxfail
  | 
  |     def test_xfail_xpassed_strict(self, testdir):
  |         item = testdir.getitem(
  |             """
  |             import pytest
  |             @pytest.mark.xfail(strict=True, reason="nope" …[4858 ch omitted]…           assert 1
  |         """
  |         )
  |         result = testdir.runpytest(p, "-rxX")
  |         result.stdout.fnmatch_lines(["*XFAIL*test_this*", "*XPASS*test_that*"])
  | 
  |     def test_dynamic_xfail_no_run(self, testdir):
  |         p = testdir.makepyfile(
  |             """
  |             import pytest
  |             @pytest.fixture
  |             def arg(request):
  | 
  RESULT: exit 0
  |                 pass
  |         """
  |         )
  |         rec = testdir.inline_run()
  |         rec.assertoutcome(skipped=1)
  | 
  |     def test_arg_as_reason(self, testdir):
  |         testdir.makepyfile(
  |             """
  |             import pytest
  |             @pytest.mark.skip('testing stuff')
  |             def test_bar():
  |                 pass
  |         """
  |        …[2674 ch omitted]…      **{
  |             "tests/test_1.py": """
  |         import pytest
  |         @pytest.mark.skip()
  |         def test_pass():
  |             pass
  |             """,
  |         }
  |     )
  |     result = testdir.runpytest("-rs", "tests/test_1.py", "--rootdir=tests")
  |     result.stdout.fnmatch_lines(
  |         ["SKIPPED [[]1[]] tests/test_1.py:2: unconditional skip"]
  |     )
  | 
[step 7] CALL bash: {"command": "cd /tmp && rm -rf repro && mkdir repro && cd repro && cat > test_it.py <<'EOF'\nimport pytest\n@pytest.mark.skip\ndef test_skip_location() -> None:\n    assert 0\nEOF\ncd /tmp/repro && python -m pytest -rs test_it.py 2>&1 | head -10 && echo \"=== with runxfail ===\" && python -m pytest -rs --runxfail test_it.py 2>&1 | head -10"}
  RESULT: exit 0
  | ============================= test session starts ==============================
  | platform linux -- Python 3.9.20, pytest-5.4.1.dev593+ge6e300e72, py-1.11.0, pluggy-0.13.1
  | rootdir: /tmp/repro
  | collected 1 item
  | 
  | test_it.py s                                                             [100%]
  | 
  | =========================== short test summary info = …[352 ch omitted]… ir: /tmp/repro
  | collected 1 item
  | 
  | test_it.py s                                                             [100%]
  | 
  | =========================== short test summary info ============================
  | SKIPPED [1] ../../testbed/src/_pytest/skipping.py:239: unconditional skip
  | ============================== 1 skipped in 0.00s ==============================
  | 
[step 8] CALL bash: {"command": "cd /testbed && python -m pytest testing/test_skipping.py -q 2>&1 | tail -5"}
  RESULT: exit 0
  | ........................................................................ [ 93%]
  | .....                                                                    [100%]
  | 77 passed in 1.27s
  | 
[step 9] CALL bash: {"command": "cd /testbed && grep -n \"def pytest_runtest_makereport\\|outcome\\|skip\" src/_pytest/runner.py | head -30"}
  RESULT: exit 0
  | 30:from _pytest.outcomes import Exit
  | 31:from _pytest.outcomes import Skipped
  | 32:from _pytest.outcomes import TEST_OUTCOME
  | 193:        elif report.skipped:
  | 194:            return "skipped", "s", "SKIPPED"
  | 312:def pytest_runtest_makereport(item: Item, call: CallInfo[None]) -> TestReport:
  | 321:        outcome = "passed"  # type: Literal["passed", "skipped", "failed"]
  | 323:        skip_exceptions = [Skipped]
  | 327:            skip_exceptions.append(unittest.SkipTest)  # type: ignore
  | 328:        if call.excinfo.errisinstance(tuple(skip_exceptions)):
  | 329:            outcome = "skipped"
  | 336:            outcome = "failed"
  | 342:    rep = CollectReport(collector.nodeid, outcome, longrepr, result)
  | 
[step 10] CALL bash: {"command": "cd /testbed && sed -n 300,360p src/_pytest/runner.py"}
  RESULT: exit 0
  |             duration=duration,
  |             when=when,
  |             result=result,
  |             excinfo=excinfo,
  |         )
  | 
  |     def __repr__(self) -> str:
  |         if self.excinfo is None:
  |             return "<CallInfo when={!r} result: {!r}>".format(self.when, self._result)
  |         return "<CallInfo when={!r} excinfo={!r}>".format(self.when, se …[1792 ch omitted]… , finalizer: Callable[[], object], colitem) -> None:
  |         """ attach a finalizer to the given colitem. """
  |         assert colitem and not isinstance(colitem, tuple)
  |         assert callable(finalizer)
  |         # assert colitem in self.stack  # some unit tests don't setup stack :/
  |         self._finalizers.setdefault(colitem, []).append(finalizer)
  | 
  | 
[step 11] CALL bash: {"command": "cd /testbed && grep -n \"class TestReport\\|def from_item_and_call\\|def _to_json\\|longrepr\" src/_pytest/reports.py | head -30 && sed -n '/def from_item_and_call/,/return rep/p' src/_pytest/reports.py"}
  RESULT: exit 0
  | 61:    longrepr = None  # type: Optional[Any]
  | 77:        longrepr = self.longrepr
  | 78:        if longrepr is None:
  | 81:        if hasattr(longrepr, "toterminal"):
  | 82:            longrepr.toterminal(out)
  | 85:                out.line(longrepr)
  | 87:                out.line("<unprintable longrepr>")
  | 95:    def longreprtext(self) -> str:
  | 98:        o …[8661 ch omitted]…            reprfileloc=reprfileloc,
  |                 style=data["style"],
  |             )  # type: Union[ReprEntry, ReprEntryNative]
  |         elif entry_type == "ReprEntryNative":
  |             reprentry = ReprEntryNative(data["lines"])
  |         else:
  |             _report_unserialization_failure(entry_type, TestReport, reportdict)
  |         return reprentry
  | 
[step 12] CALL edit_file: {"path": "/testbed/src/_pytest/skipping.py", "old": "    elif item.config.option.runxfail:\n        pass  # don't interfere\n    elif call.excinfo and isinstance(call.excinfo.value, xfail.Exception):\n        assert call.excinfo.value.msg is not None\n        rep.wasxfail = \"reason: \" + call.excinfo.value.msg\n        rep.outcome = \"skipped\"\n    elif not rep.skipped and xfailed:\n        if c …[2562 ch omitted]
  RESULT: edited /testbed/src/_pytest/skipping.py
[step 13] CALL bash: {"command": "cd /tmp/repro && python -m pytest -rs --runxfail test_it.py 2>&1 | tail -6"}
[step 14] CALL bash: {"command": "cd /testbed && python -m pytest testing/test_skipping.py -q 2>&1 | tail -5"}
  RESULT: exit 0
  | 
  | test_it.py s                                                             [100%]
  | 
  | =========================== short test summary info ============================
  | SKIPPED [1] test_it.py:2: unconditional skip
  | ============================== 1 skipped in 0.00s ==============================
  | 
  RESULT: exit 0
  | ........................................................................ [ 93%]
  | .....                                                                    [100%]
  | 77 passed in 1.32s
  | 
[step 15] CALL bash: {"command": "cd /tmp/repro && cat > test_skipif.py <<'EOF'\nimport sys\nimport pytest\n@pytest.mark.skipif(sys.platform == \"linux\", reason=\"linux only skip\")\ndef test_skipif_location():\n    assert 0\nEOF\npython -m pytest -rs --runxfail test_skipif.py 2>&1 | tail -4 && echo \"--- without runxfail ---\" && python -m pytest -rs test_skipif.py 2>&1 | tail -4"}
[step 16] CALL bash: {"command": "cd /testbed && python -m pytest testing/test_skipping.py testing/test_terminal.py testing/test_xdist.py -q 2>&1 | tail -5"}
  RESULT: exit 0
  | 
  | =========================== short test summary info ============================
  | SKIPPED [1] test_skipif.py:3: linux only skip
  | ============================== 1 skipped in 0.01s ==============================
  | --- without runxfail ---
  | 
  | =========================== short test summary info ============================
  | SKIPPED [1] test_skipif.py:3: linux only skip
  | ============================== 1 skipped in 0.00s ==============================
  | 
  RESULT: exit 0
  | ERROR: file not found: testing/test_xdist.py
  | 
  | 
  | no tests ran in 0.00s
  | 
[step 17] CALL bash: {"command": "cd /testbed && python -m pytest testing/test_skipping.py testing/test_terminal.py testing/test_runner.py testing/test_reporting.py -q 2>&1 | tail -5"}
  RESULT: exit 0
  | ERROR: file not found: testing/test_reporting.py
  | 
  | 
  | no tests ran in 0.00s
  | 
[step 18] CALL bash: {"command": "cd /testbed && python -m pytest testing/test_skipping.py testing/test_terminal.py testing/test_runner.py -q 2>&1 | tail -5"}
  RESULT: exit 0
  | =========================== short test summary info ============================
  | FAILED testing/test_terminal.py::test_color_yes - Failed: fnmatch: '\x1b[[]1m...
  | FAILED testing/test_terminal.py::TestCodeHighlight::test_code_highlight_simple
  | FAILED testing/test_terminal.py::TestCodeHighlight::test_code_highlight_continuation
  | 3 failed, 267 passed, 7 skipped, 1 xfailed, 3 warnings in 5.55s
  | 
[step 19] CALL bash: {"command": "cd /testbed && git stash && python -m pytest testing/test_terminal.py::test_color_yes testing/test_terminal.py::TestCodeHighlight::test_code_highlight_simple testing/test_terminal.py::TestCodeHighlight::test_code_highlight_continuation -q 2>&1 | tail -6 && git stash pop"}
  RESULT: exit 0
  | Saved working directory and index state WIP on pico-base: 9eb67199d SWE-bench
  | [31m============================== [31m[1m1 failed[0m[31m in 0.00s[0m[31m ===============================[0m
  | =========================== short test summary info ============================
  | FAILED testing/test_terminal.py::test_color_yes - Failed: fnmatch:  …[200 ch omitted]… ranch pico-base
  | Changes not staged for commit:
  |   (use "git add <file>..." to update what will be committed)
  |   (use "git restore <file>..." to discard changes in working directory)
  | 	modified:   src/_pytest/skipping.py
  | 
  | no changes added to commit (use "git add" and/or "git commit -a")
  | Dropped refs/stash@{0} (62528981d3e86eb909b2042dfea0252d5f787c20)
  | 
[step 20] CALL read_file: {"path": "/testbed/src/_pytest/skipping.py", "offset": 260, "limit": 50}
  RESULT:    260	@hookimpl(hookwrapper=True)
  |    261	def pytest_runtest_makereport(item: Item, call: CallInfo[None]):
  |    262	    outcome = yield
  |    263	    rep = outcome.get_result()
  |    264	    xfailed = item._store.get(xfailed_key, None)
  |    265	    # unittest special case, see setting of unexpectedsuccess_key
  |    266	    if unexpectedsuccess_key in item._stor …[1777 ch omitted]… S(strict)] " + xfailed.reason
  |    303	            else:
  |    304	                rep.outcome = "passed"
  |    305	                rep.wasxfail = xfailed.reason
  |    306	
  |    307	
  |    308	def pytest_report_teststatus(report: BaseReport) -> Optional[Tuple[str, str, str]]:
  |    309	    if hasattr(report, "wasxfail"):
  | [file has 314 lines; continue with offset=310]
[step 21] CALL bash: {"command": "cd /testbed && grep -n \"class Skipped\\|class XFailed\\|class OutcomeException\\|class Failed\\|class Exit\" src/_pytest/outcomes.py && sed -n '/^class Skipped/,/^class /p' src/_pytest/outcomes.py | head -20"}
  RESULT: exit 0
  | 27:class OutcomeException(BaseException):
  | 54:class Skipped(OutcomeException):
  | 69:class Failed(OutcomeException):
  | 75:class Exit(Exception):
  | 159:class XFailed(Failed):
  | class Skipped(OutcomeException):
  |     # XXX hackish: on 3k we fake to live in the builtins
  |     # in order to have Skipped exception printing shorter/nicer
  |     __module__ = "builtins"
  | 
  |     def __init__(
  |         self,
  |         msg: Optional[str] = None,
  |         pytrace: bool = True,
  |         allow_module_level: bool = False,
  |     ) -> None:
  |         OutcomeException.__init__(self, msg=msg, pytrace=pytrace)
  |         self.allow_module_level = allow_module_level
  | 
  | 
  | class Failed(OutcomeException):
  | 
[step 22] CALL bash: {"command": "cd /testbed && grep -n \"^skip\\|^xfail\\|Skipped\\|XFailed\" src/_pytest/outcomes.py | tail -10"}
  RESULT: exit 0
  | 54:class Skipped(OutcomeException):
  | 56:    # in order to have Skipped exception printing shorter/nicer
  | 122:@_with_exception(Skipped)
  | 143:    raise Skipped(msg=msg, allow_module_level=allow_module_level)
  | 159:class XFailed(Failed):
  | 163:@_with_exception(XFailed)
  | 175:    raise XFailed(reason)
  | 212:            raise Skipped(reason, allow_module_level=True) from None
  | 222:            raise Skipped(
  | 
[step 23] CALL bash: {"command": "cd /testbed && git diff"}
[step 24] CALL bash: {"command": "cd /testbed && python -m pytest testing/test_skipping.py testing/test_runner.py testing/test_junitxml.py testing/test_skipping.py -q 2>&1 | tail -4"}
  RESULT: exit 0
  | diff --git a/src/_pytest/skipping.py b/src/_pytest/skipping.py
  | index 7bd975e5a..4b657af14 100644
  | --- a/src/_pytest/skipping.py
  | +++ b/src/_pytest/skipping.py
  | @@ -270,6 +270,18 @@ def pytest_runtest_makereport(item: Item, call: CallInfo[None]):
  |          else:
  |              rep.longrepr = "Unexpected success"
  |          rep.outcome = "failed"
  | +    …[1133 ch omitted]… l display
  | -        # the location of where the skip exception was raised within pytest
  | -        _, _, reason = rep.longrepr
  | -        filename, line = item.reportinfo()[:2]
  | -        assert line is not None
  | -        rep.longrepr = str(filename), line + 1, reason
  |  
  |  
  |  def pytest_report_teststatus(report: BaseReport) -> Optional[Tuple[str, str, str]]:
  | 
  RESULT: exit 0
  | =========================== short test summary info ============================
  | ERROR testing/test_junitxml.py
  | !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
  | 1 error in 0.18s
  | 
[step 25] CALL bash: {"command": "cd /testbed && python -m pytest testing/test_junitxml.py -q 2>&1 | tail -8"}
[step 26] CALL bash: {"command": "cd /testbed && python -m pytest testing/test_skipping.py testing/test_runner.py -q 2>&1 | tail -3"}
  RESULT: exit 0
  |     return _bootstrap._gcd_import(name[level:], package, level)
  | testing/test_junitxml.py:10: in <module>
  |     import xmlschema
  | E   ModuleNotFoundError: No module named 'xmlschema'
  | =========================== short test summary info ============================
  | ERROR testing/test_junitxml.py
  | !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
  | 1 error in 0.05s
  | 
  RESULT: exit 0
  | ........................................................................ [ 54%]
  | .........................................x...................            [100%]
  | 132 passed, 1 xfailed in 2.37s
  | 
[step 27] CALL bash: {"command": "cd /testbed && python -m pytest testing/test_skipping.py -q -k \"xfail or skip\" 2>&1 | tail -3"}
[step 28] CALL bash: {"command": "cd /testbed && python -m pytest testing/test_skipping.py testing/test_doctest.py testing/test_unittest.py -q 2>&1 | tail -3"}
  RESULT: exit 0
  | ........................................................................ [ 93%]
  | .....                                                                    [100%]
  | 77 passed in 1.35s
  | 
  RESULT: exit 0
  | ...x.......................................................s............ [ 81%]
  | ..........sssssss...............................ss                       [100%]
  | 255 passed, 10 skipped, 1 xfailed in 5.11s
  | 
[step 29] CALL bash: {"command": "rm -rf /tmp/repro && cd /testbed && git status && git diff --stat"}
  RESULT: exit 0
  | On branch pico-base
  | Changes not staged for commit:
  |   (use "git add <file>..." to update what will be committed)
  |   (use "git restore <file>..." to discard changes in working directory)
  | 	modified:   src/_pytest/skipping.py
  | 
  | no changes added to commit (use "git add" and/or "git commit -a")
  |  src/_pytest/skipping.py | 24 ++++++++++++------------
  |  1 file changed, 12 insertions(+), 12 deletions(-)
  | 
# Python 3.15 compatibility

After working on astroid (see https://github.com/pylint-dev/astroid/issues/3032), I've switched to pylint to test also the astroid compatibility with testsuite in pylint. There are a couple of issues to fix, mostly in tests:

The complete patch is:

```diff
diff --git a/tests/functional/d/deprecated/deprecated_methods_py36.rc b/tests/functional/d/deprecated/deprecated_methods_py36.rc
new file mode 100644
index 0000000..e91017c
--- /dev/null
+++ b/tests/functional/d/deprecated/deprecated_methods_py36.rc
@@ -0,0 +1,2 @@
+[testoptions]
+max_pyver=3.14
diff --git a/tests/functional/n/no/no_name_in_module.315.txt b/tests/functional/n/no/no_name_in_module.315.txt
new file mode 100644
index 0000000..421094f
--- /dev/null
+++ b/tests/functional/n/no/no_name_in_module.315.txt
@@ -0,0 +1,12 @@
+no-name-in-module:5:0:5:23::No name 'tutu' in module 'collections':UNDEFINED
+no-name-in-module:6:0:6:28::No name 'toto' in module 'collections':UNDEFINED
+no-member:16:6:16:17::Module 'sys' has no 'stdoout' member; maybe 'stdout'?:INFERENCE
+no-name-in-module:23:0:23:34::No name 'compiile' in module 're':UNDEFINED
+no-name-in-module:23:0:23:34::No name 'findiiter' in module 're':UNDEFINED
+pointless-statement:26:0:26:23::Statement seems to have no effect:UNDEFINED
+no-name-in-module:34:4:34:36::No name 'anything' in module 'collections':UNDEFINED
+no-name-in-module:49:4:49:37::No name 'indeed_missing' in module 'collections':UNDEFINED
+no-name-in-module:54:4:54:27::No name 'emit' in module 'collections':UNDEFINED
+no-name-in-module:71:8:71:32::No name 'emit2' in module 'collections':UNDEFINED
+no-name-in-module:76:0:76:34::No name 'lala' in module 'functional.n.no.no_self_argument':UNDEFINED
+no-name-in-module:77:0:77:39::No name 'bla' in module 'functional.n.no.no_self_argument':UNDEFINED
diff --git a/tests/functional/n/no/no_name_in_module.py b/tests/functional/n/no/no_name_in_module.py
index 6d34245..99099f9 100644
--- a/tests/functional/n/no/no_name_in_module.py
+++ b/tests/functional/n/no/no_name_in_module.py
@@ -7,8 +7,8 @@ from collections import toto  # [no-name-in-module]
 toto.yo()
 
 from xml.etree import ElementTree
-ElementTree.nonexistent_function()  # [no-member]
-ElementTree.another.nonexistent.function()  # [no-member]
+ElementTree.nonexistent_function()  # <3.15: [no-member]
+ElementTree.another.nonexistent.function()  # <3.15: [no-member]
 
 
 import sys
diff --git a/tests/functional/u/unspecified_encoding_py38.315.txt b/tests/functional/u/unspecified_encoding_py38.315.txt
new file mode 100644
index 0000000..6b687c7
--- /dev/null
+++ b/tests/functional/u/unspecified_encoding_py38.315.txt
@@ -0,0 +1,40 @@
+unspecified-encoding:13:0:13:14::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:14:0:14:20::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:15:0:15:20::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:16:0:16:34::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:17:0:17:19::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:26:5:26:19::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:29:5:29:34::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:33:5:33:45::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:38:0:38:17::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:39:0:39:23::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:40:0:40:23::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:41:0:41:37::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:50:5:50:22::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:53:5:53:37::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:57:5:57:48::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:66:0:66:26::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:67:0:67:39::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:68:0:68:50::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:75:0:75:35::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:76:0:76:50::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:81:0:81:21::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:82:0:82:25::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:83:0:83:25::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:84:0:84:39::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:149:0:149:23::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:152:0:152:28::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:155:0:155:26::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:158:0:158:35::Using open without explicitly specifying an encoding:HIGH
+bad-open-mode:161:0:161:25::"""None"" is not a valid mode for open.":HIGH
+unspecified-encoding:161:0:161:25::Using open without explicitly specifying an encoding:HIGH
+bad-open-mode:164:0:164:19::"""2"" is not a valid mode for open.":HIGH
+unspecified-encoding:164:0:164:19::Using open without explicitly specifying an encoding:HIGH
+bad-open-mode:176:0:176:24::"""5"" is not a valid mode for open.":INFERENCE
+unspecified-encoding:176:0:176:24::Using open without explicitly specifying an encoding:HIGH
+bad-open-mode:177:0:177:27::"""5"" is not a valid mode for open.":INFERENCE
+unspecified-encoding:177:0:177:27::Using open without explicitly specifying an encoding:HIGH
+unspecified-encoding:180:5:180:29::Using open without explicitly specifying an encoding:INFERENCE
+unspecified-encoding:183:0:183:29::Using open without explicitly specifying an encoding:INFERENCE
+unspecified-encoding:186:0:186:44::Using open without explicitly specifying an encoding:INFERENCE
+unspecified-encoding:193:0:193:34::Using open without explicitly specifying an encoding:INFERENCE
diff --git a/tests/functional/u/unspecified_encoding_py38.py b/tests/functional/u/unspecified_encoding_py38.py
index 9ff2fd7..0c7a289 100644
--- a/tests/functional/u/unspecified_encoding_py38.py
+++ b/tests/functional/u/unspecified_encoding_py38.py
@@ -74,7 +74,7 @@ Path(FILENAME).write_text("string", encoding="utf8")
 LOCALE_ENCODING = None
 Path(FILENAME).write_text("string")  # [unspecified-encoding]
 Path(FILENAME).write_text("string", encoding=None)  # [unspecified-encoding]
-Path(FILENAME).write_text("string", encoding=LOCALE_ENCODING)  # [unspecified-encoding]
+Path(FILENAME).write_text("string", encoding=LOCALE_ENCODING)  # <3.15: [unspecified-encoding]
 
 LOCALE_ENCODING = locale.getlocale()[1]
 Path(FILENAME).open("w+b")
diff --git a/tests/testutils/test_functional_testutils.py b/tests/testutils/test_functional_testutils.py
index 2b1574e..6691e17 100644
--- a/tests/testutils/test_functional_testutils.py
+++ b/tests/testutils/test_functional_testutils.py
@@ -7,6 +7,7 @@
 import contextlib
 import os
 import os.path
+import sys
 import shutil
 import tempfile
 from collections.abc import Iterator
@@ -135,17 +136,19 @@ def test_minimal_messages_config_enabled(pytest_config: MagicMock) -> None:
         str(DATA_DIRECTORY / "m"), "minimal_messages_config.py"
     )
     mod_test = testutils.LintModuleTest(test_file, pytest_config)
+    expected_enabled = [
+        "consider-using-with",
+        "consider-using-f-string",
+        # Always enable fatal errors: important not to have false negatives
+        "astroid-error",
+        "fatal",
+        "syntax-error",
+    ]
+    if sys.version_info < (3, 15):
+        expected_enabled.append("unspecified-encoding")
     assert all(
         mod_test._linter.is_message_enabled(msgid)
-        for msgid in (
-            "consider-using-with",
-            "unspecified-encoding",
-            "consider-using-f-string",
-            # Always enable fatal errors: important not to have false negatives
-            "astroid-error",
-            "fatal",
-            "syntax-error",
-        )
+        for msgid in expected_enabled
     )
     assert not mod_test._linter.is_message_enabled("unused-import")
 

```

Context:
- Deprecated methods in `SourceFileLoader` and `SourcelessFileLoader` are now removed.
- New test files for Python 3.15.
- `unspecified-encoding` issues are related to [PEP 686](https://peps.python.org/pep-0686/)

import os
import shutil
import tempfile
from pathlib import Path

import testtools

from bandit.core import utils as b_utils


def _touch(path):
    """Create an empty file at ``path``."""
    Path(path).touch()


class UtilTests(testtools.TestCase):
    """This set of tests exercises bandit.core.util functions."""

    def setUp(self):
        super().setUp()
        self._setup_get_module_qualname_from_path()

    def _setup_get_module_qualname_from_path(self):
        """Setup a fake directory for testing get_module_qualname_from_path().

        Create temporary directory and then create fake .py files
        within directory structure.  We setup test cases for
        a typical module, a path misssing a middle __init__.py,
        no __init__.py anywhere in path, symlinking .py files.
        """

        self.tempdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tempdir)
        self.reltempdir = os.path.relpath(self.tempdir)

        # good/a/b/c/test_typical.py
        os.makedirs(os.path.join(self.tempdir, "good", "a", "b", "c"), 0o755)
        _touch(os.path.join(self.tempdir, "good", "__init__.py"))
        _touch(os.path.join(self.tempdir, "good", "a", "__init__.py"))
        _touch(os.path.join(self.tempdir, "good", "a", "b", "__init__.py"))
        _touch(
            os.path.join(self.tempdir, "good", "a", "b", "c", "__init__.py")
        )
        _touch(
            os.path.join(
                self.tempdir, "good", "a", "b", "c", "test_typical.py"
            )
        )

        # missingmid/a/b/c/test_missingmid.py
        os.makedirs(
            os.path.join(self.tempdir, "missingmid", "a", "b", "c"), 0o755
        )
        _touch(os.path.join(self.tempdir, "missingmid", "__init__.py"))
        # no missingmid/a/__init__.py
        _touch(
            os.path.join(self.tempdir, "missingmid", "a", "b", "__init__.py")
        )
        _touch(
            os.path.join(
                self.tempdir, "missingmid", "a", "b", "c", "__init__.py"
            )
        )
        _touch(
            os.path.join(
                self.tempdir, "missingmid", "a", "b", "c", "test_missingmid.py"
            )
        )

        # missingend/a/b/c/test_missingend.py
        os.makedirs(
            os.path.join(self.tempdir, "missingend", "a", "b", "c"), 0o755
        )
        _touch(os.path.join(self.tempdir, "missingend", "__init__.py"))
        _touch(
            os.path.join(self.tempdir, "missingend", "a", "b", "__init__.py")
        )
        # no missingend/a/b/c/__init__.py
        _touch(
            os.path.join(
                self.tempdir, "missingend", "a", "b", "c", "test_missingend.py"
            )
        )

        # syms/a/bsym/c/test_typical.py
        os.makedirs(os.path.join(self.tempdir, "syms", "a"), 0o755)
        _touch(os.path.join(self.tempdir, "syms", "__init__.py"))
        _touch(os.path.join(self.tempdir, "syms", "a", "__init__.py"))
        os.symlink(
            os.path.join(self.tempdir, "good", "a", "b"),
            os.path.join(self.tempdir, "syms", "a", "bsym"),
        )

    def test_get_module_qualname_from_path_abs_typical(self):
        """Test get_module_qualname_from_path with typical absolute paths."""

        name = b_utils.get_module_qualname_from_path(
            os.path.join(
                self.tempdir, "good", "a", "b", "c", "test_typical.py"
            )
        )
        self.assertEqual("good.a.b.c.test_typical", name)

    def test_get_module_qualname_from_path_with_dot(self):
        """Test get_module_qualname_from_path with a "." ."""

        name = b_utils.get_module_qualname_from_path(
            os.path.join(".", "__init__.py")
        )

        self.assertEqual("__init__", name)

    def test_get_module_qualname_from_path_abs_missingmid(self):
        # Test get_module_qualname_from_path with missing module
        # __init__.py

        name = b_utils.get_module_qualname_from_path(
            os.path.join(
                self.tempdir, "missingmid", "a", "b", "c", "test_missingmid.py"
            )
        )
        self.assertEqual("b.c.test_missingmid", name)

    def test_get_module_qualname_from_path_abs_missingend(self):
        # Test get_module_qualname_from_path with no __init__.py
        # last dir'''

        name = b_utils.get_module_qualname_from_path(
            os.path.join(
                self.tempdir, "missingend", "a", "b", "c", "test_missingend.py"
            )
        )
        self.assertEqual("test_missingend", name)

    def test_get_module_qualname_from_path_abs_syms(self):
        """Test get_module_qualname_from_path with symlink in path."""

        name = b_utils.get_module_qualname_from_path(
            os.path.join(
                self.tempdir, "syms", "a", "bsym", "c", "test_typical.py"
            )
        )
        self.assertEqual("syms.a.bsym.c.test_typical", name)

    def test_get_module_qualname_from_path_rel_typical(self):
        """Test get_module_qualname_from_path with typical relative paths."""
        for path in (
            os.path.join(self.reltempdir, "good", "__init__.py"),
            os.path.join(self.reltempdir, "good", "a", "__init__.py"),
            os.path.join(self.reltempdir, "good", "a", "b", "__init__.py"),
            os.path.join(self.reltempdir, "good", "a", "b", "c", "__init__.py"),
        ):
            self.assertTrue(os.path.exists(path), path)

        name = b_utils.get_module_qualname_from_path(
            os.path.join(
                self.reltempdir, "good", "a", "b", "c", "test_typical.py"
            )
        )
        self.assertEqual("good.a.b.c.test_typical", name)

    def test_get_module_qualname_from_path_rel_missingmid(self):
        # Test get_module_qualname_from_path with module __init__.py
        # missing and relative paths
        for path in (
            os.path.join(self.reltempdir, "missingmid", "a", "b", "__init__.py"),
            os.path.join(self.reltempdir, "missingmid", "a", "b", "c", "__init__.py"),
        ):
            self.assertTrue(os.path.exists(path), path)

        name = b_utils.get_module_qualname_from_path(
            os.path.join(
                self.reltempdir,
                "missingmid",
                "a",
                "b",
                "c",
                "test_missingmid.py",
            )
        )
        self.assertEqual("b.c.test_missingmid", name)

    def test_get_module_qualname_from_path_rel_missingend(self):
        # Test get_module_qualname_from_path with __init__.py missing from
        # last dir and using relative paths

        name = b_utils.get_module_qualname_from_path(
            os.path.join(
                self.reltempdir,
                "missingend",
                "a",
                "b",
                "c",
                "test_missingend.py",
            )
        )
        self.assertEqual("test_missingend", name)

    def test_get_module_qualname_from_path_rel_syms(self):
        """Test get_module_qualname_from_path with symbolic relative paths."""
        for path in (
            os.path.join(self.reltempdir, "syms", "__init__.py"),
            os.path.join(self.reltempdir, "syms", "a", "__init__.py"),
            os.path.join(self.reltempdir, "syms", "a", "bsym", "__init__.py"),
            os.path.join(self.reltempdir, "syms", "a", "bsym", "c", "__init__.py"),
        ):
            self.assertTrue(os.path.exists(path), path)

        name = b_utils.get_module_qualname_from_path(
            os.path.join(
                self.reltempdir, "syms", "a", "bsym", "c", "test_typical.py"
            )
        )
        self.assertEqual("syms.a.bsym.c.test_typical", name)

    def test_get_module_qualname_from_path_sys(self):
        """Test get_module_qualname_from_path with system module paths."""

        name = b_utils.get_module_qualname_from_path(os.__file__)
        self.assertEqual("os", name)

        # This will fail because of magic for os.path. Not sure how to fix.
        # name = b_utils.get_module_qualname_from_path(os.path.__file__)
        # self.assertEqual(name, 'os.path')

    def test_get_module_qualname_from_path_invalid_path(self):
        """Test get_module_qualname_from_path with invalid path."""

        name = b_utils.get_module_qualname_from_path("/a/b/c/d/e.py")
        self.assertEqual("e", name)

    def test_get_module_qualname_from_path_dir(self):
        """Test get_module_qualname_from_path with dir path."""

        self.assertRaises(
            b_utils.InvalidModulePath,
            b_utils.get_module_qualname_from_path,
            "/tmp/",
        )

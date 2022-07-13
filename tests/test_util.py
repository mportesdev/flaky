import os
import shutil
import tempfile
from pathlib import Path

import testtools

from bandit.core import utils as b_utils


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

        self.tempdir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tempdir)
        self.reltempdir = Path(os.path.relpath(self.tempdir))
        reltempdir_resolved = self.reltempdir.resolve()
        self.assertEqual(
            self.tempdir,
            reltempdir_resolved,
            f'self.tempdir: {self.tempdir}\n'
            f'\ncwd: {Path.cwd()}\n'
            f'self.reltempdir: {self.reltempdir}\n'
            f'reltempdir_resolved: {reltempdir_resolved}\n'
            'self.tempdir not equal to reltempdir_resolved'
        )

        # good/a/b/c/test_typical.py
        (self.tempdir / "good" / "a" / "b" / "c").mkdir(parents=True)
        (self.tempdir / "good" / "__init__.py").touch()
        (self.tempdir / "good" / "a" / "__init__.py").touch()
        (self.tempdir / "good" / "a" / "b" / "__init__.py").touch()
        (self.tempdir / "good" / "a" / "b" / "c" / "__init__.py").touch()
        (self.tempdir / "good" / "a" / "b" / "c" / "test_typical.py").touch()

        # missingmid/a/b/c/test_missingmid.py
        (self.tempdir / "missingmid" / "a" / "b" / "c").mkdir(parents=True)
        (self.tempdir / "missingmid" / "__init__.py").touch()
        # no missingmid/a/__init__.py
        (self.tempdir / "missingmid" / "a" / "b" / "__init__.py").touch()
        (self.tempdir / "missingmid" / "a" / "b" / "c" / "__init__.py").touch()
        (self.tempdir / "missingmid" / "a" / "b" / "c" / "test_missingmid.py").touch()

        # syms/a/bsym/c/test_typical.py
        (self.tempdir / "syms" / "a").mkdir(parents=True)
        (self.tempdir / "syms" / "__init__.py").touch()
        (self.tempdir / "syms" / "a" / "__init__.py").touch()
        os.symlink(
            self.tempdir / "good" / "a" / "b",
            self.tempdir / "syms" / "a" / "bsym",
        )

    def test_get_module_qualname_from_path_rel_typical(self):
        """Test get_module_qualname_from_path with typical relative paths."""
        for path in (
            self.reltempdir / "good" / "__init__.py",
            self.reltempdir / "good" / "a" / "__init__.py",
            self.reltempdir / "good" / "a" / "b" / "__init__.py",
            self.reltempdir / "good" / "a" / "b" / "c" / "__init__.py",
        ):
            self.assertTrue(path.exists(), path)

        name = b_utils.get_module_qualname_from_path(
            self.reltempdir / "good" / "a" / "b" / "c" / "test_typical.py"
        )
        self.assertEqual("good.a.b.c.test_typical", name)

    def test_get_module_qualname_from_path_rel_missingmid(self):
        # Test get_module_qualname_from_path with module __init__.py
        # missing and relative paths
        for path in (
            self.reltempdir / "missingmid" / "a" / "b" / "__init__.py",
            self.reltempdir / "missingmid" / "a" / "b" / "c" / "__init__.py",
        ):
            self.assertTrue(path.exists(), path)

        name = b_utils.get_module_qualname_from_path(
            self.reltempdir / "missingmid" / "a" / "b" / "c" / "test_missingmid.py"
        )
        self.assertEqual("b.c.test_missingmid", name)

    def test_get_module_qualname_from_path_rel_syms(self):
        """Test get_module_qualname_from_path with symbolic relative paths."""
        for path in (
            self.reltempdir / "syms" / "__init__.py",
            self.reltempdir / "syms" / "a" / "__init__.py",
            self.reltempdir / "syms" / "a" / "bsym" / "__init__.py",
            self.reltempdir / "syms" / "a" / "bsym" / "c" / "__init__.py",
        ):
            self.assertTrue(path.exists(), path)

        name = b_utils.get_module_qualname_from_path(
            self.reltempdir / "syms" / "a" / "bsym" / "c" / "test_typical.py"
        )
        self.assertEqual("syms.a.bsym.c.test_typical", name)

import unittest
import os
import tempfile
import shutil
from mygit_core.repository import init, MYGIT_DIR
from mygit_core.index import add_file, get_staged_files, clear_index


class TestIndex(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        init()

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def _make_file(self, filename, content):
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)
        return filepath

    def test_add_file_appears_in_index(self):
        """After add_file, the file must appear in get_staged_files()."""
        self._make_file("hello.txt", "hello")
        add_file("hello.txt")
        staged = get_staged_files()
        self.assertIn("hello.txt", staged)

    def test_add_file_records_correct_hash(self):
        """The hash recorded in index must match the file's actual SHA1."""
        from mygit_core.hash_object import hash_file
        self._make_file("hello.txt", "hello")
        add_file("hello.txt")
        staged = get_staged_files()
        self.assertEqual(staged["hello.txt"], hash_file("hello.txt"))

    def test_restage_updates_hash(self):
        """Re-staging a modified file must update the hash in index."""
        self._make_file("hello.txt", "version one")
        add_file("hello.txt")
        first_hash = get_staged_files()["hello.txt"]

        # Overwrite the file with new content
        with open("hello.txt", "w") as f:
            f.write("version two")

        add_file("hello.txt")
        second_hash = get_staged_files()["hello.txt"]

        self.assertNotEqual(first_hash, second_hash)

    def test_add_nonexistent_file_does_not_crash(self):
        """Staging a file that doesn't exist must print an error, not crash."""
        try:
            add_file("ghost.txt")
        except Exception as e:
            self.fail(f"add_file raised an exception on missing file: {e}")

    def test_clear_index_empties_staging_area(self):
        """After clear_index, get_staged_files must return an empty dict."""
        self._make_file("hello.txt", "hello")
        add_file("hello.txt")
        self.assertTrue(get_staged_files())

        clear_index()
        self.assertEqual(get_staged_files(), {})

    def test_multiple_files_staged(self):
        """Staging two files must add both to index."""
        self._make_file("a.txt", "aaa")
        self._make_file("b.txt", "bbb")
        add_file("a.txt")
        add_file("b.txt")
        staged = get_staged_files()
        self.assertIn("a.txt", staged)
        self.assertIn("b.txt", staged)
        self.assertEqual(len(staged), 2)
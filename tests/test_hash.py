import unittest
import os
import tempfile
import shutil
from mygit_core.repository import init, MYGIT_DIR
from mygit_core.hash_object import hash_file, store_object, restore_object


class TestHashObject(unittest.TestCase):

    def setUp(self):
        """
        Before each test: create a real temporary directory and
        switch into it so .mygit/ is isolated per test.
        """
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        init()

    def tearDown(self):
        """
        After each test: go back to original directory
        and delete the temp directory entirely.
        """
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def _make_file(self, filename, content):
        """Helper: write a file in the test directory."""
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)
        return filepath

    def test_same_content_same_hash(self):
        """Two files with identical content must produce identical hashes."""
        f1 = self._make_file("a.txt", "hello world")
        f2 = self._make_file("b.txt", "hello world")
        self.assertEqual(hash_file(f1), hash_file(f2))

    def test_different_content_different_hash(self):
        """Even a one-character difference must produce a different hash."""
        f1 = self._make_file("a.txt", "hello world")
        f2 = self._make_file("b.txt", "hello world!")
        self.assertNotEqual(hash_file(f1), hash_file(f2))

    def test_hash_is_40_chars(self):
        """SHA1 hex digest is always exactly 40 characters."""
        f = self._make_file("a.txt", "test content")
        result = hash_file(f)
        self.assertEqual(len(result), 40)

    def test_store_object_creates_blob(self):
        """store_object must save the file content into .mygit/objects/."""
        f = self._make_file("a.txt", "store this")
        file_hash = store_object(f)
        blob_path = os.path.join(self.test_dir, MYGIT_DIR, "objects", file_hash)
        self.assertTrue(os.path.exists(blob_path))

    def test_store_object_returns_correct_hash(self):
        """store_object must return the same hash as hash_file."""
        f = self._make_file("a.txt", "consistent hash")
        self.assertEqual(store_object(f), hash_file(f))

    def test_store_object_deduplication(self):
        """Storing the same content twice must not create duplicate blobs."""
        f1 = self._make_file("a.txt", "same content")
        f2 = self._make_file("b.txt", "same content")
        h1 = store_object(f1)
        h2 = store_object(f2)
        self.assertEqual(h1, h2)
        objects_dir = os.path.join(self.test_dir, MYGIT_DIR, "objects")
        self.assertEqual(len(os.listdir(objects_dir)), 1)

    def test_restore_object_reconstructs_file(self):
        """restore_object must write back the exact original content."""
        f = self._make_file("original.txt", "restore me exactly")
        file_hash = store_object(f)

        destination = os.path.join(self.test_dir, "restored.txt")
        restore_object(file_hash, destination)

        with open(destination, "r") as out:
            self.assertEqual(out.read(), "restore me exactly")
import unittest
import os
import json
import tempfile
import shutil
from mygit_core.repository import init, get_mygit_path, MYGIT_DIR
from mygit_core.index import add_file
from mygit_core.commit import create_commit, get_current_head


class TestCommit(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        init()

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def _make_and_stage(self, filename, content):
        """Helper: write a file and stage it in one call."""
        with open(filename, "w") as f:
            f.write(content)
        add_file(filename)

    def test_commit_creates_json_file(self):
        """A successful commit must create a .json file in commits/."""
        self._make_and_stage("a.txt", "hello")
        create_commit("initial commit")

        commits_dir = get_mygit_path("commits")
        files = os.listdir(commits_dir)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith(".json"))

    def test_commit_updates_head(self):
        """HEAD must point to the new commit hash after committing."""
        self._make_and_stage("a.txt", "hello")
        create_commit("initial commit")

        head = get_current_head()
        self.assertIsNotNone(head)
        self.assertEqual(len(head), 40)

    def test_commit_clears_index(self):
        """After commit, the staging area must be empty."""
        from mygit_core.index import get_staged_files
        self._make_and_stage("a.txt", "hello")
        create_commit("initial commit")
        self.assertEqual(get_staged_files(), {})

    def test_commit_updates_log(self):
        """Each commit must add one entry to log.json."""
        self._make_and_stage("a.txt", "hello")
        create_commit("first")
        self._make_and_stage("b.txt", "world")
        create_commit("second")

        with open(get_mygit_path("log.json"), "r") as f:
            log = json.load(f)

        self.assertEqual(len(log), 2)
        self.assertEqual(log[0]["message"], "second")
        self.assertEqual(log[1]["message"], "first")

    def test_commit_with_nothing_staged_does_not_crash(self):
        """Committing with empty staging area must fail gracefully."""
        try:
            create_commit("empty commit")
        except Exception as e:
            self.fail(f"create_commit raised an exception with nothing staged: {e}")

    def test_second_commit_has_parent(self):
        """The second commit's parent field must equal the first commit's hash."""
        self._make_and_stage("a.txt", "hello")
        create_commit("first")
        first_hash = get_current_head()

        self._make_and_stage("b.txt", "world")
        create_commit("second")
        second_hash = get_current_head()

        commit_path = get_mygit_path("commits", f"{second_hash}.json")
        with open(commit_path, "r") as f:
            commit = json.load(f)

        self.assertEqual(commit["parent"], first_hash)

    def test_commit_stores_correct_files(self):
        """The commit JSON must record the exact files that were staged."""
        self._make_and_stage("a.txt", "hello")
        create_commit("test files")
        head = get_current_head()

        commit_path = get_mygit_path("commits", f"{head}.json")
        with open(commit_path, "r") as f:
            commit = json.load(f)

        self.assertIn("a.txt", commit["files"])
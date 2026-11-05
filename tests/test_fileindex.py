import tempfile
import unittest
from pathlib import Path
from fileindex import index,search,compare,digest


class FileIndexTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root=Path(self.directory.name)
        (self.root/"note.txt").write_text("hello",encoding="utf-8")
    def test_index(self):
        self.assertEqual(index(self.root)["count"],1)
    def test_relative_path(self):
        self.assertEqual(index(self.root)["files"][0]["path"],"note.txt")
    def test_hash(self):
        self.assertEqual(len(index(self.root,True)["files"][0]["sha256"]),64)
    def test_search(self):
        self.assertEqual(len(search(index(self.root),query="NOTE")),1)
    def test_extension(self):
        self.assertEqual(len(search(index(self.root),extension=".csv")),0)
    def test_min_size(self):
        self.assertEqual(len(search(index(self.root),min_size=6)),0)
    def test_added(self):
        before=index(self.root)
        (self.root/"new.csv").write_text("a,b",encoding="utf-8")
        self.assertEqual(compare(before,index(self.root))["added"],["new.csv"])
    def test_removed(self):
        before=index(self.root)
        (self.root/"note.txt").unlink()
        self.assertEqual(compare(before,index(self.root))["removed"],["note.txt"])


if __name__=="__main__":
    unittest.main()

import os
import sys
import unittest
cwd = os.getcwd()
sys.path.append("../..")
from BlenderMhwModelImporter.common.fileOperations import DeleteBytes, createContentStream, contentStreams

class TestFileOperations(unittest.TestCase):
    def testDeleteBytes(self):
        x = createContentStream(b"test")
        DeleteBytes(x,1,2)
        self.assertEqual(b"tt", contentStreams[x].read())


if __name__ == '__main__':
    unittest.main()

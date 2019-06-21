import unittest
import sapaths
import ivpaths

import imp
imp.reload(sapaths)
imp.reload(ivpaths)

"""
class TestSAPath(unittest.TestCase):

    def test_lc_paths(self):
        paths = sapaths.SAPaths()
        paths.load_nodes_from_directory(r"E:\Output\LC")
        self.assertNotEqual(paths, None)
        
    def test_sa_paths(self):
        paths = sapaths.SAPaths()
        paths.load_nodes_from_directory(r"E:\scripts\Vanilla\Compiled\SA")
        self.assertNotEqual(paths, None)

"""
class TestIVPath(unittest.TestCase):

    def test_iv_paths(self):
        paths = ivpaths.IVPaths()
        paths.load_nodes_from_directory(r"E:\scripts\IVPaths")
        self.assertNotEqual(paths, None)

if __name__ == '__main__':
    paths = ivpaths.IVPaths()
    paths.load_nodes_from_directory(r"E:\scripts\IVPaths")
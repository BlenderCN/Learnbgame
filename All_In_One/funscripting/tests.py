import unittest

class TestFoo(unittest.TestCase):
    def test_true(self):
        self.assertEqual('foo'.upper(), 'FOO')

if __name__ == '__main__':
    unittest.main()

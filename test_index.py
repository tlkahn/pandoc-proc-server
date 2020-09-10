import unittest
import index

class TestCleanFunction(unittest.TestCase):

    def test_clean(self):
      str = '[[somewebsite.url][hello\nworld]]'
      self.assertEqual(index.clean(str), '[[somewebsite.url][hello world]]')
      str = '[[somewebsite.url]]'
      self.assertEqual(index.clean(str), '')
      str = '** hello'
      self.assertEqual(index.clean(str), '*** hello')
if __name__ == '__main__':
    unittest.main()
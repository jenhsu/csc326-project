from __future__ import absolute_import

import os
import signal
import sys
import subprocess
import time
import unittest

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from crawler import crawler


class CrawlerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Launch the bottle test server once for all tests."""
        cls.server_process = subprocess.Popen(['python', 'test_server.py'])
        # Simple time-based wait for server to finish launching.
        # A more rigorous approach may be used in the future.
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        """Shut down the bottle test server after testing completion."""
        os.kill(cls.server_process.pid, signal.SIGINT)

    def setUp(self):
        """Run the crawler before each unit test."""
        self.crawler = crawler(None, "test_urls.txt")

    def tearDown(self):
        """Reset the crawler after each unit test."""
        self.crawler = None

    def test_inverted_index(self):
        """Test inverted index against ground truth."""
        expected = {
            1: set([1]), 2: set([1, 2, 3]), 3: set([1, 2]), 4: set([1, 2, 3]),
            5: set([1, 2, 3]), 6: set([1]), 7: set([1]), 8: set([1]),
            9: set([1]), 10: set([1, 3]), 11: set([1, 3]), 12: set([1]),
            13: set([3]), 14: set([3]), 15: set([3]), 16: set([3]),
            17: set([3]), 18: set([3]), 19: set([2]), 20: set([2]),
            21: set([2]), 22: set([2]), 23: set([2]), 24: set([2]),
            25: set([2])
        }
        inverted_index = self.crawler.get_inverted_index()
        self.assertEqual(inverted_index, expected,
                         "Inverted index does not match ground truth.")

    def test_resolved_inverted_index(self):
        """Test resolved inverted index against ground truth."""
        expected = {
            u'600': set([u'http://localhost:8080/two']),
            u'just': set(['http://localhost:8080/']),
            u'testing': set(['http://localhost:8080/']),
            u'700': set([u'http://localhost:8080/two']),
            u'one': set(['http://localhost:8080/', u'http://localhost:8080/one']),
            u'if': set([u'http://localhost:8080/one']),
            u'-': set(['http://localhost:8080/']),
            u'two': set(['http://localhost:8080/', u'http://localhost:8080/two', u'http://localhost:8080/one']),
            u'400': set([u'http://localhost:8080/two']),
            u'you': set([u'http://localhost:8080/one']),
            u'finish': set([u'http://localhost:8080/one']),
            u'300': set([u'http://localhost:8080/two']),
            u'never': set([u'http://localhost:8080/one']),
            u'link': set(['http://localhost:8080/', u'http://localhost:8080/two', u'http://localhost:8080/one']),
            u'word_four': set(['http://localhost:8080/']),
            u'100': set([u'http://localhost:8080/two']),
            u'mystery': set([u'http://localhost:8080/one']),
            u'900': set([u'http://localhost:8080/two']),
            u'novel': set([u'http://localhost:8080/one']),
            u'word': set(['http://localhost:8080/', u'http://localhost:8080/two']),
            u'this': set(['http://localhost:8080/']),
            u'three': set(['http://localhost:8080/', u'http://localhost:8080/two']),
            u'every': set([u'http://localhost:8080/one']),
            u'root': set(['http://localhost:8080/']),
            u'page': set(['http://localhost:8080/', u'http://localhost:8080/two', u'http://localhost:8080/one'])
        }
        resolved_inverted_index = self.crawler.get_resolved_inverted_index()
        self.assertEqual(resolved_inverted_index, expected,
                         "Resolved Inverted Index does not match ground truth.")


if __name__ == '__main__':
    unittest.main()

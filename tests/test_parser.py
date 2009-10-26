
import unittest
import os

class TestParser(unittest.TestCase):

    def setUp(self):
        self.base = os.path.dirname(os.path.abspath(__file__))
        self.fixtures = os.path.join(self.base, 'fixtures')
        self.demo_feed = os.path.join(self.fixtures, 'github.rss')

    def testFetchFeed(self):
        from aggregator.feeds import fetch
        content, encoding = fetch(self.demo_feed)
        self.assertEquals(len(content), 66574)
        self.assertEquals(encoding, 'ascii')


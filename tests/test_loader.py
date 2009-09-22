
import unittest
import os

from aggregator.opml import *

class TestLoader(unittest.TestCase):

    def setUp(self):
        self.base = os.path.dirname(os.path.abspath(__file__))
        self.fixtures = os.path.join(self.base, 'fixtures')
        self.valid_opml = os.path.join(self.fixtures, 'sample-opml.xml')
        self.invalid_opml = os.path.join(self.fixtures, 'invalid-opml.xml')
        self.greader_opml = os.path.join(self.fixtures, 'google-reader-subscriptions.xml')

    def testValidOpml(self):
        OpmlLoader(self.valid_opml).assert_valid()

    def testInvalidOpml(self):
        assert not OpmlLoader(self.invalid_opml).is_valid()

    def testLoadRealFile(self):
        OpmlLoader(self.greader_opml).assert_valid()


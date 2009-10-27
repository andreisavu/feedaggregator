
import unittest
import os

from aggregator.db.schema import *
from aggregator.feeds import aggregate

from test_settings import *


class TestAggregator(unittest.TestCase):

    def setUp(self):
        self.hbase = create_client(HBASE_THRIFT_HOST, HBASE_THRIFT_PORT)
        initdb(self.hbase, 'test_')

        self.base = os.path.dirname(os.path.abspath(__file__))
        self.fixtures = os.path.join(self.base, 'fixtures')
        self.demo_feed = os.path.join(self.fixtures, 'github.rss')

    def tearDown(self):
        dropdb(self.hbase, 'test_')
        self.hbase = None

    def testAggregateSingleFeed(self):
        aggregate(self.hbase, self.demo_feed, 'blogs', 'test_')
     
    

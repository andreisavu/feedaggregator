
import unittest
import os

from aggregator.db.schema import *
from test_settings import *

class TestSchema(unittest.TestCase):
    
    def setUp(self):
        self.hbase = create_client(HBASE_THRIFT_HOST, HBASE_THRIFT_PORT)

    def tearDown(self):
        self.dropAllTestTables()
        self.hbase = None

    def dropAllTestTables(self):
        tables = self.hbase.getTableNames()
        for table in tables:
            if 'test_' in table:
                self.hbase.disableTable(table)
                self.hbase.deleteTable(table)

    def testInitDb(self):
        initdb(self.hbase, 'test_')
        tables = self.hbase.getTableNames()
        for table in ['test_Urls', 'test_Feeds', 'test_UrlsIndex']:
            self.assertTrue(table in tables)


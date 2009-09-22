#! /usr/bin/env python

from datetime import datetime

from pyhbase import *
from settings import *

def handle_url(client, url, updated):
    dt = datetime.fromtimestamp(updated)
    key = 'all/%s' % dt.isoformat()
    client.mutateRow('UrlsIndex', key, [Mutation(column='Url:0', value=url)])
    

if __name__ == '__main__':
    client = create_client(HBASE_THRIFT_HOST, HBASE_THRIFT_PORT)
    scanner = Scanner(client, 'Urls', ['Meta:'])
    for row in scanner:
        if 'Meta:updated' in row.columns:
            print 'Indexing %s ...' % row.row
            handle_url(client, row.row, float(row.columns['Meta:updated'].value))


#! /usr/bin/env python

import sys

from time import time
from datetime import datetime
from PyRSS2Gen import RSS2, RSSItem

from pyhbase import *
from settings import *

def latest24h():
    client = create_client(HBASE_THRIFT_HOST, HBASE_THRIFT_PORT)

    dt = datetime.fromtimestamp(time() - 24*60*60)
    key = 'all/%s' % dt.isoformat()

    scanner = Scanner(client, 'UrlsIndex', ['Url:'], start_row=key)
    for row in scanner:
        url = client.getRow('Urls', row.columns['Url:0'].value)
        yield url[0]

if __name__ == '__main__':
    items = []
    for url in latest24h():
        items.append(RSSItem(
            title = url.columns['Content:title'].value,
            link = url.row,
            description = url.columns['Content:raw'].value,
            pubDate = datetime.fromtimestamp(float(url.columns['Meta:updated'].value))
        ))
    rss = RSS2(
        title = 'Aggregated feed',
        link = 'http://example.com/rss',
        description = 'Hbase aggregated feed',
        lastBuildDate = datetime.now(),
        items = items
    )

    rss.write_xml(sys.stdout)


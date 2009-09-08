#! /usr/bin/env python

import feedparser
import time
import codecs

from pyhbase import *
from settings import *

def handle_feed(content, lasthit):
    data = feedparser.parse(content)
    codec = codecs.lookup('ascii')
    for entry in data.entries:
        client = create_client(HBASE_THRIFT_HOST, HBASE_THRIFT_PORT)
        url = entry.link
        title = entry.title
        try:
            content, length = codec.encode(entry.content[0].value, 'replace')
        except UnicodeError: 
            continue
 
        data = [
            Mutation(column='Content:raw', value=content),
            Mutation(column='Content:title', value=title),
            Mutation(column='Meta:updated', value=str(time.mktime(entry.updated_parsed)))
        ]
        try:
            print 'Adding %s ..' % url
            client.mutateRow('Urls', url, data)
        except Exception, e:
            print 'Hbase feed entry push failed. Ignoring.', e
        except KeyboardInterrupt:
            continue

if __name__ == '__main__':
    client = create_client(HBASE_THRIFT_HOST, HBASE_THRIFT_PORT)
    scanner = Scanner(client, 'Feeds', ['Content:raw', 'Meta:'])
    for row in scanner:
        if 'Meta:lasthit' in row.columns:
            try:
                handle_feed(row.columns['Content:raw'].value, float(row.columns['Meta:lasthit'].value))
            except AttributeError:
                pass



#! /usr/bin/env python

import sys

from pyhbase import *
from settings import *
from feedaggregator import *

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: ./opml-loader.py opml_file'
        sys.exit(1)

    loader = OpmlLoader(sys.argv[1])
    if not loader.is_valid():
        print 'Validation failed for opml file'
        sys.exit(2)

    client = create_client(HBASE_THRIFT_HOST, HBASE_THRIFT_PORT)
    for element in loader:
        data = [
            Mutation(column='Meta:type', value=element.type),
            Mutation(column='Meta:title', value=element.title),
            Mutation(column='Meta:htmlUrl', value=element.htmlUrl)
        ]
        print 'Adding "%s"' % element.htmlUrl
        try:
            client.mutateRow('Feeds', element.xmlUrl, data)
        except (IOError, IllegalArgument, UnicodeError):
            print 'Hbase mutation failed.'
        except:
            client = create_client(HBASE_THRIFT_HOST, HBASE_THRIFT_PORT)
            print 'Hbase mutation failed. Unknow error'


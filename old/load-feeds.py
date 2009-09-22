#! /usr/bin/env python

from urllib import urlopen
from time import time

from pyhbase import *
from settings import *

def download_all(client):
    scanner = Scanner(client, 'Feeds', ['Meta:htmlUrl', 'Meta:lasthit'])
    for row in scanner:
        if 'Meta:lasthit' in row.columns: continue
        url = row.row
        try:
            print 'Downloading %s ...' % url
            content = urlopen(url).read()
            data = [
                Mutation(column='Content:raw', value=content), 
                Mutation(column='Meta:lasthit', value=str(time()))
            ]
            client.mutateRow('Feeds', url, data)
        except (IOError, IllegalArgument):
            print 'Feed download failed.'
        except:
            print 'Unknown error. Skipping...'

if __name__ == '__main__':
    client = create_client(HBASE_THRIFT_HOST, HBASE_THRIFT_PORT)
    while True:
        try:
            download_all(client)
            break
        except Exception, e:
            print e


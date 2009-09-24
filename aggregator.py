#! /usr/bin/env python
"""
Yet another feed aggregator. 

A hase sample application.
"""

import sys
import time
import logging as log

from optparse import OptionParser
from datetime import datetime

from aggregator import db
from aggregator import feeds

from aggregator.threadpool import ThreadPool
from aggregator.opml import OpmlLoader
from aggregator.util import smart_str, any_in, split_csv

from settings import *

def dispatch(opts, args):
    """ Analyze command line parameters end call the needed function """
    client = get_hbase_client()
    if opts.initdb is True:
        db.schema.initdb(client)

    elif opts.resetdb is True:
        db.schema.dropdb(client)
        db.schema.initdb(client)

    elif opts.feed is not None:
        feeds.aggregate(client, opts.feed, opts.cat or "")

    elif opts.refresh_feeds is True:
        refresh_feeds(client, opts.cat or "")

    elif opts.opml is not None:
        aggregate_opml(client, opts.opml, opts.cat or "")

    elif opts.file is not None:
        aggregate_file(client, opts.file, opts.cat or "")

    elif opts.list is True:
        dump_urls(client, opts.hours, opts.cat or "")

def parse_cli():
    """ Setup CLI parser and use it """
    parser = OptionParser()

    parser.add_option('', '--initdb', action="store_true", 
        dest="initdb", default=False, help="init database")
    parser.add_option('', '--resetdb', action="store_true",
        dest="resetdb", default=False, help="reset database")
    parser.add_option('-r', '--refresh-feeds', action="store_true",
        dest="refresh_feeds", default=False, help="refresh all feeds or just a category")
    parser.add_option('', '--opml', dest="opml", 
        help="aggregate feeds from opml FILE", metavar="FILE")
    parser.add_option('-f', '--feed', dest="feed",
        help="parse FEED and add to index", metavar="FEED")
    parser.add_option('', '--file', dest='file',
        help="load feeds from FILE. one url per line", metavar="FILE")
    parser.add_option('', '--cat', dest="cat",
        help="feed CATEGORIES. csv format in quotes", metavar="CATEGORIES")
    parser.add_option('', '--hours', dest="hours",
        help="how many HOURS back in time", metavar="HOURS")
    parser.add_option('-l', '--list', action="store_true", dest='list',
        help="dump a list of urls from the aggregated feeds", default=False)
    parser.add_option('-w', '--webui', action="store_true",
        dest="webui", default=False, help="start simple web interface")
    
    return parser.parse_args()

def get_hbase_client():
    log.info('Connecting to Hbase Host:%s, Port:%s' % (HBASE_THRIFT_HOST, HBASE_THRIFT_PORT))
    try:
        return db.create_client(HBASE_THRIFT_HOST, HBASE_THRIFT_PORT)
    except Exception:
        log.critical('HBase connection failed')
        sys.exit(1)

def dump_urls(client, hours, cat):
    if hours is None: hours = 24
    if cat == '': cat = '__all__'

    hours = int(hours)
    dt = datetime.fromtimestamp(time.time() - hours*60*60)
    start_row = '%s/%s' % (cat, dt.isoformat())

    scanner = db.Scanner(client, 'UrlsIndex', ['Url:'], start_row)
    for row in scanner:
        print row.columns['Url:'].value

def refresh_feeds(client, allowed_categs):
    """
    Refresh all feeds found in the database using a pool of threads. 
    """
    log.info('Starting to refresh all feeds')
    allowed_categs = split_csv(allowed_categs)
    def read_data():
        scanner = db.Scanner(client, 'Feeds', ['Meta:'])
        for row in scanner:
            feed, categs = row.row, row.columns['Meta:categs'].value
            if allowed_categs and not any_in(split_csv(categs), allowed_categs):
                continue
            yield feed, categs
    feeds.aggregate_all(client, read_data(), get_hbase_client)

def aggregate_file(client, file_path, categs):
    """
    Aggregate all links from a text file
    """
    log.info('Loading from file: %s' % file_path)
    def read_data():
        file = open(file_path)
        for url in file.xreadlines():
            yield url.strip(), categs
    feeds.aggregate_all(client, read_data(), get_hbase_client)

def aggregate_opml(client, file, categs):
    """
    Aggregate all links from an OPML file
    """ 
    log.info('Loading from file: %s' % file)
    def read_data():
        loader = OpmlLoader(file)
        if not loader.is_valid():
            log.error('Invalid opml file: %s' % file)
            return
        for element in loader:
            yield element.xmlUrl, categs
    feeds.aggregate_all(client, read_data(), get_hbase_client)

if __name__ == '__main__':
    log.basicConfig(level=log.INFO)
    opts, args = parse_cli()
    dispatch(opts, args)



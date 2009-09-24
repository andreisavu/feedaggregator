#! /usr/bin/env python
"""
Yet another feed aggregator. 

A hase sample application.
"""

from aggregator import db
from aggregator.threadpool import ThreadPool
from aggregator.opml import OpmlLoader
from settings import *

import sys
import time
import logging as log

from optparse import OptionParser
from datetime import datetime

def dispatch(opts, args):
    """ Analyze command line parameters end call the needed function """
    client = get_hbase_client()
    if opts.initdb is True:
        initdb(client)
    elif opts.resetdb is True:
        dropdb(client)
        initdb(client)
    elif opts.feed is not None:
        aggregate_feed(client, opts.feed, opts.cat or "")
    elif opts.refresh_feeds is True:
        refresh_feeds(client, opts.cat or "")
    elif opts.opml is not None:
        aggregate_opml(client, opts.opml, opt.cat or "")

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
    parser.add_option('', '--cat', dest="cat",
        help="feed CATEGORIES. csv format in quotes", metavar="CATEGORIES")
    parser.add_option('', '--hours', dest="hours",
        help="how many HOURS back in time", metavar="HOURS")
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

def initdb(client):
    create_feeds_table(client)
    create_urls_table(client)
    create_urlsindex_table(client)

def dropdb(client):
    tables = client.getTableNames()
    if 'Urls' in tables:
        log.info('Removing table `Urls`')
        client.disableTable('Urls')
        client.deleteTable('Urls');
    if 'Feeds' in tables:
        log.info('Removing table `Feeds`')
        client.disableTable('Feeds')
        client.deleteTable('Feeds')
    if 'UrlsIndex' in tables:
        log.info('Removing table `UrlsIndex`')
        client.disableTable('UrlsIndex')
        client.deleteTable('UrlsIndex')

def create_feeds_table(client):
    try:
        log.info('Creating `Feeds` table')
        client.createTable('Feeds', [
            db.ColumnDescriptor(name='Content'),
            db.ColumnDescriptor(name='Meta', maxVersions=1)])
    except db.AlreadyExists:
        log.error('Table `Feeds` alread exists.')

def create_urls_table(client):
    try:
        log.info('Creating `Urls` table')
        client.createTable('Urls', [
            db.ColumnDescriptor(name='Content'),
            db.ColumnDescriptor(name='Meta', maxVersions=1)])
    except db.AlreadyExists:
        log.error('Table `Urls` alread exists.')

def create_urlsindex_table(client):
    try:
        log.info('Creating `UrlsIndex` table')
        client.createTable('UrlsIndex', [
            db.ColumnDescriptor(name='Url', maxVersions=1)])
    except db.AlreadyExists:
        log.error('Table `UrlsIndex` alread exists.')

def attach_connection(thread):
    thread.hbase = get_hbase_client()
    return thread

def any_in(needles, haystack):
    for x in needles:
        if x in haystack: return True
    return False

def parse_categories(cats):
    return [x.strip() for x in cats.split(',')]

def refresh_feeds(client, allowed_categs):
    """
    Refresh all feeds found in the database using a pool of threads. 
    """
    log.info('Starting to refresh all feeds')
    scanner = db.Scanner(client, 'Feeds', ['Meta:'])

    allowed_categs = parse_categories(allowed_categs)
    pool = ThreadPool(20, thread_init=attach_connection) 
    for row in scanner:
        feed, categs = row.row, row.columns['Meta:categs'].value
        if not any_in(parse_categories(categs), allowed_categs):
            continue
        pool.queueTask(lambda worker, p:aggregate_feed(worker.hbase, *p), (feed, categs))
    pool.joinAll()

def aggregate_opml(client, file, categs):
    """
    Aggregate all links from an OPML file
    """
    loader = OpmlLoader(file)
    if not loader.is_valid():
        log.error('Invalid opml file: %s' % file)
        return

    log.info('Loading from file: %s' % file)
    pool = ThreadPool(20, thread_init=attach_connection)
    for element in loader:
        pool.queueTask(lambda worker, p:aggregate_feed(worker.hbase, *p), (element.xmlUrl, categs))
    pool.joinAll()

def aggregate_feed(client, feed, categs=""):
    """
    Fetch feed content, parse it and generate all the needed indexes.
    """
    try:
        content, encoding = fetch_feed(feed)
        save_feed(client, feed, content, encoding, categs)
        save_urls(client, content, encoding, categs)
    except (IOError, db.IllegalArgument), e:
        log.error(e)


def fetch_feed(feed):
    """
    Fetch feed and detect charset. The return result is a  byte string and
    the encoding information.
    """
    from urllib import urlopen
    import chardet
    
    log.info("Fetching feed '%s'" % feed)
    content = urlopen(feed).read()

    d = chardet.detect(content)
    log.info("Detected charset: %s" % d['encoding'])

    return smart_str(content, d['encoding'], 'replace'), str(d['encoding'])

def save_feed(client, feed, content, encoding, categs):
    log.info("Pushing content to hbase 'Feeds' table")
    data = [
        db.Mutation(column='Content:raw', value=content),
        db.Mutation(column='Meta:lasthit', value=str(time.time())),
        db.Mutation(column='Meta:encoding', value=encoding),
        db.Mutation(column='Meta:categs', value=str(categs))
    ]
    client.mutateRow('Feeds', feed, data)

def save_urls(client, content, encoding, categs):
    import feedparser
    log.info('Parsing feed content')
    data = feedparser.parse(content)
    for entry in data.entries:
        url, title = entry.link, entry.title
        if 'content' in entry:
            content = entry.content[0].value
        else:
            content = ''

        log.info("Adding & indexing: '%s'" % url)
        if 'updated_parsed' not in entry or entry.updated_parsed is None:
            continue
        t = time.mktime(entry.updated_parsed)
        data = [
            db.Mutation(column='Content:raw', value=smart_str(content, encoding)),
            db.Mutation(column='Content:title', value=smart_str(title, encoding)),
            db.Mutation(column='Meta:updated', value=str(t))
        ]
        client.mutateRow('Urls', url, data)

        # XXX warning : avoid having collisions
        key = datetime.fromtimestamp(t).isoformat()
        parts = set([x.strip() for x in categs.split(',')])
        parts.add('__all__')
        for cat in parts:
            row = '%s/%s' % (cat,key)
            client.mutateRow('UrlsIndex', row, [db.Mutation(column='Url', value=smart_str(url))])

def smart_str(s, encoding='utf-8', errors='replace'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.
    """
    if not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s

if __name__ == '__main__':
    log.basicConfig(level=log.INFO)
    opts, args = parse_cli()
    dispatch(opts, args)



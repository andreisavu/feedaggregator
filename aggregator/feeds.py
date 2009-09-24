
import logging as log
import time

from datetime import datetime

import db

from threadpool import ThreadPool
from util import smart_str

def aggregate(hbase, feed, categs=""):
    """
    Aggregate one feed. Fetch, parse and add to index table
    """
    try:
        content, encoding = fetch(feed)
        save_feed(hbase, feed, content, encoding, categs)
        extract_urls(hbase, content, encoding, categs)
    except (IOError, db.IllegalArgument), e:
        log.error(e)

def aggregate_all(client, iterator, connection_factory):
    """
    Aggregate all feeds returned by the generator.

    The generator should contain pairs of two elements (feed_url, categories)
    """
    def attach_connection(thread):
        thread.hbase = connection_factory()
        return thread
    pool = ThreadPool(10, thread_init=attach_connection) 
    for feed, categs in iterator:
        pool.queueTask(lambda worker, p:aggregate(worker.hbase, *p), (feed, categs))
    pool.joinAll()

def fetch(feed):
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

def extract_urls(client, content, encoding, categs):
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



#! /usr/bin/env python
"""
Yet another feed aggregator. 

A hase sample application.
"""

from aggregator import db
from settings import *

import sys
import logging as log

from optparse import OptionParser

def dispatch(opts, args):
    """ Analyze command line parameters end call the needed function """
    if opts.initdb is True:
        initdb()
    elif opts.resetdb is True:
        dropdb()
        initdb()

def parse_cli():
    """ Setup CLI parser and use it """
    parser = OptionParser()

    parser.add_option('', '--initdb', action="store_true", 
        dest="initdb", default=False, help="init database")
    parser.add_option('', '--resetdb', action="store_true",
        dest="resetdb", default=False, help="reset database")
    parser.add_option('-r', '--refresh-feeds', action="store_true",
        dest="refresh_feeds", default=False, help="refresh all feeds")
    parser.add_option('', '--opml', dest="opml", 
        help="aggregate feeds from opml FILE", metavar="FILE")
    parser.add_option('-f', '--feed', dest="feed",
        help="parse FEED and add to index", metavar="FEED")
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

def initdb(client=None):
    client = get_hbase_client()
    create_feeds_table(client)
    create_urls_table(client)
    create_urlsindex_table(client)

def dropdb():
    client = get_hbase_client()
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

if __name__ == '__main__':
    log.basicConfig(level=log.INFO)
    opts, args = parse_cli()
    print opts
    dispatch(opts, args)



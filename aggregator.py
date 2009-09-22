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

def initdb():
    client = get_hbase_client()

if __name__ == '__main__':
    log.basicConfig(level=log.INFO)
    opts, args = parse_cli()
    print opts
    dispatch(opts, args)



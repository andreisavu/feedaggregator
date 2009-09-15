#! /usr/bin/env python
"""
Yet another feed aggregator. 
"""

from optparse import OptionParser

def main():
    opts, args = parse_cli()
    print opts

def parse_cli():
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

if __name__ == '__main__':
    main()


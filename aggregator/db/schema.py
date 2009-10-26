
import logging as log

from pyhbase import *

def initdb(client, prefix=''):
    """
    Create all database tables needed.
    """
    create_feeds_table(client, prefix)
    create_urls_table(client, prefix)
    create_urlsindex_table(client, prefix)

def dropdb(client, prefix=''):
    """
    Drop all aggregator related tables.
    """
    tables = client.getTableNames()
 
    urls_table= '%sUrl' % prefix
    if urls_table in tables:
        log.info('Removing table `%s`' % urls_table)
        client.disableTable(urls_table)
        client.deleteTable(urls_table);

    feeds_table = '%sFeeds' % prefix
    if feeds_table in tables:
        log.info('Removing table `%s`' % feeds_table)
        client.disableTable(feeds_table)
        client.deleteTable(feeds_table)

    urlsindex_table = '%sUrlsIndex' % prefix
    if urlsindex_table in tables:
        log.info('Removing table `%s`' % urlsindex_table)
        client.disableTable(urlsindex_table)
        client.deleteTable(urlsindex_table)

def create_feeds_table(client, prefix=''):
    """
    Create the table used for storing feed content.

    For each feed we store the latest 3 versions and some aditional metadata.
    """
    feeds_table = '%sFeeds' % prefix
    try:
        log.info('Creating `%s` table' % feeds_table)
        client.createTable(feeds_table, [
            ColumnDescriptor(name='Content'),
            ColumnDescriptor(name='Meta', maxVersions=1)])
    except AlreadyExists:
        log.error('Table `%s` alread exists.' % feeds_table)

def create_urls_table(client, prefix=''):
    """
    Create the table need for urls.

    For each url we store 3 versions of content and metadata.
    """
    urls_table = '%sUrls' % prefix
    try:
        log.info('Creating `%s` table' % urls_table)
        client.createTable(urls_table, [
            ColumnDescriptor(name='Content'),
            ColumnDescriptor(name='Meta', maxVersions=1)])
    except AlreadyExists:
        log.error('Table `%s` alread exists.' % urls_table)

def create_urlsindex_table(client, prefix=''):
    """
    Create main index table.

    Based on this table we can generate a global aggregated feed
    that can be filtered by category.
    """
    urlsindex_table = '%sUrlsIndex' % prefix
    try:
        log.info('Creating `%s` table' % urlsindex_table)
        client.createTable(urlsindex_table, [
            ColumnDescriptor(name='Url', maxVersions=1)])
    except AlreadyExists:
        log.error('Table `%s` alread exists.' % urlsindex_table)



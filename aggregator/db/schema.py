
import logging as log
from pyhbase import *

def initdb(client):
    """
    Create all database tables needed.
    """
    create_feeds_table(client)
    create_urls_table(client)
    create_urlsindex_table(client)

def dropdb(client):
    """
    Drop all aggregator related tables.
    """
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
    """
    Create the table used for storing feed content.

    For each feed we store the latest 3 versions and some aditional metadata.
    """
    try:
        log.info('Creating `Feeds` table')
        client.createTable('Feeds', [
            ColumnDescriptor(name='Content'),
            ColumnDescriptor(name='Meta', maxVersions=1)])
    except AlreadyExists:
        log.error('Table `Feeds` alread exists.')

def create_urls_table(client):
    """
    Create the table need for urls.

    For each url we store 3 versions of content and metadata.
    """
    try:
        log.info('Creating `Urls` table')
        client.createTable('Urls', [
            ColumnDescriptor(name='Content'),
            ColumnDescriptor(name='Meta', maxVersions=1)])
    except AlreadyExists:
        log.error('Table `Urls` alread exists.')

def create_urlsindex_table(client):
    """
    Create main index table.

    Based on this table we can generate a global aggregated feed
    that can be filtered by category.
    """
    try:
        log.info('Creating `UrlsIndex` table')
        client.createTable('UrlsIndex', [
            ColumnDescriptor(name='Url', maxVersions=1)])
    except AlreadyExists:
        log.error('Table `UrlsIndex` alread exists.')




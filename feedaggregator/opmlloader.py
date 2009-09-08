
import opml
import os

from lxml import etree

class OpmlLoader(object):
    
    def __init__(self, file, validate=True):
        self.file = file
        self.pkg_base = os.path.dirname(os.path.abspath(__file__))
        self.schema_file = os.path.join(self.pkg_base, 'schemas', 'opml.xsd')

    def __iter__(self):
        outline = opml.parse(self.file)
        return iter(outline)

    def is_valid(self):
        try:
            self.assert_valid()
            return True
        except etree.DocumentInvalid:
            return False

    def assert_valid(self):
        schema = etree.XMLSchema(file=open(self.schema_file))
        doc = etree.parse(open(self.file))
        schema.assertValid(doc)


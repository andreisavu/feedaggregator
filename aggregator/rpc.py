
import logging as log

from SimpleXMLRPCServer import SimpleXMLRPCServer

class Aggregator(object):
    """
    XML-RPC endpoints for aggregator functionality.

    Why xmlrpc? Easy integration with any kind of external service and UI. 
    """
    def __init__(self, client):
        self.client = client

    def get_feeds_list(self):
        return []

    def aggregate(feed):
        return False

def start(client):
    """
    Start aggregator rpc server on default port
    """
    server = SimpleXMLRPCServer(('0.0.0.0', 8000))
    server.register_introspection_functions()
    server.register_instance(Aggregator(client))
    try:
        log.info("Starting xmlrpc server on port 8000")
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Exiting.")
        
    


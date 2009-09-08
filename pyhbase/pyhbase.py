
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from hbase import Hbase
from hbase.ttypes import *

def create_client(host, port):
    transport = TSocket.TSocket(host, port)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    client = Hbase.Client(protocol)
    transport.open()
    return client

class Scanner(object):
    """
    Simple row scanner. 

    This object is iterable. 
    """

    def __init__(self, client, table, columns, start_row=''):
        self._client = client
        self._table = table
        self._columns = columns
        self._start_row = start_row 
    
    def get_rows(self):
        sid = self._client.scannerOpen(self._table, self._start_row, self._columns)
        try:
            while True:
                yield self._client.scannerGet(sid)
        except NotFound:
            raise StopIteration()
        finally:
            self._client.scannerClose(sid)

    def __iter__(self):
        return iter(self.get_rows())


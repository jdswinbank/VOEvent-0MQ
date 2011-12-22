# ZeroMQ transport definition.
# John Swinbank, <swinbank@transientskp.org>, 2011.

# ZeroMQ
import zmq

# XML parsing using ElementTree
import xml.etree.ElementTree as ElementTree

# Twisted
from twisted.python import log

# Local configuration
from config import VOEVENT_ROLES

class ZMQManager(object):
    """
    The ZMQManager receives XML elements and forwards them (or otherwise) to
    an ZeroMQ pubsub system.
    """
    def __init__(self, host, port, hwm=5):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.setsockopt(zmq.HWM, hwm)
        self.socket.bind("tcp://%s:%d" % (host, port))

    def handle(self, data):
        """
        Logic to decide whether data (an XML element) should be rebroadcast is
        implemented here.

        Note that it should be serialized to a string before rebroadcasting.
        """
        if data.get('role') in VOEVENT_ROLES:
            log.msg("Rebroadcasting to ZeroMQ")
            self.socket.send(ElementTree.tostring(data))

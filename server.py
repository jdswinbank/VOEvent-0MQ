# Simple VOEvent listener.
# John Swinbank, <swinbank@transientskp.org>, 2011.

# Python standard library
import sys

# XML parsing using ElementTree
import xml.etree.ElementTree as ElementTree

# Twisted
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import Int32StringReceiver
from twisted.python import log
from twisted.internet import reactor

# ZeroMQ
import zmq

# Utilities for constructing transport protocol messages
import transportmessage

# Configuration
from config import REMOTE_HOST
from config import REMOTE_PORT
from config import ZMQ_HOST
from config import ZMQ_PORT
from config import ALIVE_ROLES
from config import VOEVENT_ROLES

class ZMQManager(object):
    def __init__(self, host, port, hwm=5):
        # Set up our ZeroMQ context
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.setsockopt(zmq.HWM, hwm)
        self.socket.bind("tcp://%s:%d" % (host, port))

    def handle(self, data):
        if data.get('role') in VOEVENT_ROLES:
            self.socket.send(data)

class VOEventProto(Int32StringReceiver):
    """
    Implements the VOEvent Transport Protocol; see
    <http://www.ivoa.net/Documents/Notes/VOEventTransport/>.

    All messages are preceded by a 4-byte network ordered payload size
    followed by the payload data. Twisted's Int32StringReceiver handles this
    for us automatically.

    When a VOEvent is received, we broadcast it onto a ZeroMQ PUB socket.
    """
    def __init__(self, zmq_manager):
        self.zmq_manager = zmq_manager

    def stringReceived(self, data):
        """
        Called when a complete new message is received.

        We have two jobs here:

        1. Forward the message to the ZeroMQ system;
        2. Reply according to the Transport Protocol.
        """
        try:
            incoming = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received")
            return

        # We have some parseable XML, so hand it off to ZeroMQ.
        zmq_manager.handle(incoming)

        # And reply if appropriate.
        # The root element of both VOEvent and Transport packets has a
        # "role" element which we use to identify the type of message we
        # have received.
        if incoming.get('role') in ALIVE_ROLES:
            log.msg("IAmAlive received")
            outgoing = transportmessage.IAmAliveResponse(incoming.find('Origin').text)
        elif incoming.get('role') in VOEVENT_ROLES:
            log.msg("VOEvent received")
            outgoing = transportmessage.Ack(incoming.attrib['ivorn'])
        else:
            log.err("Incomprehensible data received")

        try:
            self.sendString(outgoing.to_string())
            log.msg("Sent response")
        except NameError:
            log.msg("No response to send")

class VOEventProtoFactory(ReconnectingClientFactory):
    def __init__(self, zmq_manager):
        self.zmq_manager = zmq_manager

    def buildProtocol(self, addr):
        self.resetDelay()
        return VOEventProto(zmq_manager)

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    zmq_manager = ZMQManager(ZMQ_HOST, ZMQ_PORT)
    reactor.connectTCP(REMOTE_HOST, REMOTE_PORT, VOEventProtoFactory(zmq_manager))
    reactor.run()

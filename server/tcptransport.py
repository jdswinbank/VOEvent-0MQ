# VOEvent TCP transport protocol using Twisted.
# John Swinbank, <swinbank@transientskp.org>, 2011.

# XML parsing using ElementTree
import xml.etree.ElementTree as ElementTree

# Twisted protocol definition
from twisted.python import log
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet.protocol import ReconnectingClientFactory

# Constructors for transport protocol messages
from messages import IAmAliveResponse
from messages import Ack

# Local configuration
from config import ALIVE_ROLES
from config import VOEVENT_ROLES

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

        1. Reply according to the Transport Protocol.
        2. Forward the message to the ZeroMQ system;
        """
        try:
            incoming = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received")
            return

        # Handle our transport protocol obligations.
        # The root element of both VOEvent and Transport packets has a
        # "role" element which we use to identify the type of message we
        # have received.
        if incoming.get('role') in ALIVE_ROLES:
            log.msg("IAmAlive received")
            outgoing = IAmAliveResponse(incoming.find('Origin').text)
        elif incoming.get('role') in VOEVENT_ROLES:
            log.msg("VOEvent received")
            outgoing = Ack(incoming.attrib['ivorn'])
        else:
            log.err("Incomprehensible data received")
        try:
            self.sendString(outgoing.to_string())
            log.msg("Sent response")
        except NameError:
            log.msg("No response to send")

        # And hand the data off to the ZeroMQ system.
        self.zmq_manager.handle(incoming)


class VOEventProtoFactory(ReconnectingClientFactory):
    def __init__(self, zmq_manager):
        self.zmq_manager = zmq_manager

    def buildProtocol(self, addr):
        self.resetDelay()
        return VOEventProto(self.zmq_manager)

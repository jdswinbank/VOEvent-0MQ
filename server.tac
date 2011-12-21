# Simple VOEvent listener.
# John Swinbank, <swinbank@transientskp.org>, 2011.

# This is a Twisted application; run it using twistd:
#
# $ twistd -ny server.tac

# XML parsing using ElementTree
import xml.etree.ElementTree as ElementTree

# Twisted
from twisted.application.service import Application
from twisted.application.internet import TCPClient
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import Int32StringReceiver
from twisted.python import log

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

# Set up our ZeroMQ context
zmq_context = zmq.Context()
zmq_socket = zmq_context.socket(zmq.PUB)
zmq_socket.setsockopt(zmq.HWM, 5)
zmq_socket.bind("tcp://%s:%d" % (ZMQ_HOST, ZMQ_PORT))

class VOEventProto(Int32StringReceiver):
    """
    Implements the VOEvent Transport Protocol; see
    <http://www.ivoa.net/Documents/Notes/VOEventTransport/>.

    All messages are preceded by a 4-byte network ordered payload size
    followed by the payload data. Twisted's Int32StringReceiver handles this
    for us automatically.

    When a VOEvent is received, we broadcast it onto a ZeroMQ PUB socket.
    """
    def stringReceived(self, data):
        """
        Called when a complete new message is received.
        """
        try:
            incoming = ElementTree.fromstring(data)
            # The root element of both VOEvent and Transport packets has a
            # "role" element which we use to identify the type of message we
            # have received.
            if incoming.get('role') in ALIVE_ROLES:
                log.msg("IAmAlive received")
                outgoing = transportmessage.IAmAliveResponse(incoming.find('Origin').text)
            elif incoming.get('role') in VOEVENT_ROLES:
                log.msg("VOEvent received")
                outgoing = transportmessage.Ack(incoming.attrib['ivorn'])
                zmq_socket.send(data)
            else:
                log.err("Incomprehensible data received")
        except ElementTree.ParseError:
            log.err("Unparsable message")
        try:
            self.sendString(outgoing.to_string())
            log.msg("Sent response")
        except NameError:
            log.msg("No response to send")

class VOEventProtoFactory(ReconnectingClientFactory):
    def buildProtocol(self, addr):
        self.resetDelay()
        return VOEventProto()

application = Application("VOEvent Listener")
service = TCPClient(REMOTE_HOST, REMOTE_PORT, VOEventProtoFactory())
service.setServiceParent(application)

# Simple VOEvent listener.
# John Swinbank, <swinbank@transientskp.org>, 2011.

# This is a Twisted application; run it using twistd:
#
# $ twistd -ny voevent.tac

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

# Construct our transport messages
import transportmessage

# Configuration
REMOTE_HOST = "voevent.dc3.com"
REMOTE_PORT = 8099
ZMQ_HOST = "*"
ZMQ_PORT = 8089
ALIVE_ROLES = ("iamalive")
VOEVENT_ROLES = ('observation', 'prediction', 'utility', 'test')

# Set up our ZeroMQ context
zmq_context = zmq.Context()
zmq_socket = zmq_context.socket(zmq.PUB)
zmq_socket.setsockopt(zmq.HWM, 5)
zmq_socket.bind("tcp://%s:%d" % (ZMQ_HOST, ZMQ_PORT))

class VOEventProto(Int32StringReceiver):
    def connectionMade(self):
        log.msg("connection made")

    def stringReceived(self, data):
        try:
            incoming = ElementTree.fromstring(data)
            if incoming.get('role') in ALIVE_ROLES:
                log.msg("Got iamalive")
                outgoing = transportmessage.IAmAliveResponse(incoming.find('Origin').text)
            elif incoming.get('role') in VOEVENT_ROLES:
                log.msg("Got VOEvent")
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

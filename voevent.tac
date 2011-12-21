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

# Construct our transport messages
import transportmessage

remote_host = "voevent.dc3.com"
remote_port = 8099

class VOEventProto(Int32StringReceiver):
    def connectionMade(self):
        log.msg("connection made")

    def stringReceived(self, data):
        try:
            incoming = ElementTree.fromstring(data)
            log.msg("Data received")
            print ElementTree.tostring(incoming)
            if incoming.get('role') == "iamalive":
                log.msg("Got iamalive")
                outgoing = transportmessage.IAmAliveResponse(incoming.find('Origin').text)
            elif incoming.tag[-7:] == "VOEvent":
                log.msg("Got VOEvent")
                outgoing = transportmessage.Ack(incoming.attrib['ivorn'])
            else:
                log.err("Incomprehensible data received")
        except ElementTree.ParseError:
            log.err("Unparsable message")
        try:
            self.sendString(outgoing.to_string())
        except NameError:
            log.msg("No response to send")

class VOEventProtoFactory(ReconnectingClientFactory):
    def buildProtocol(self, addr):
        self.resetDelay()
        return VOEventProto()

application = Application("VOEvent Listener")
service = TCPClient(remote_host, remote_port, VOEventProtoFactory())
service.setServiceParent(application)

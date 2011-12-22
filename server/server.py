# Forward VOEvents to ZeroMQ.
# John Swinbank, <swinbank@transientskp.org>, 2011.

# Python standard library
import sys

# Twisted
from twisted.python import log
from twisted.internet import reactor

# Transport protocol definitions
from tcptransport import VOEventProtoFactory
from zeromqtransport import ZMQManager

# Local configuration
from config import REMOTE_HOST, REMOTE_PORT
from config import ZMQ_HOST, ZMQ_PORT

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    zmq_manager = ZMQManager(ZMQ_HOST, ZMQ_PORT)
    reactor.connectTCP(REMOTE_HOST, REMOTE_PORT, VOEventProtoFactory(zmq_manager))
    reactor.run()

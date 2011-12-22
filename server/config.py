# VOEvent -> ZeroMQ configuration.
# John Swinbank, <swinbank@transientskp.org>, 2011.

# This is quick and dirty!
LOCAL_IVO = "ivo://lofar/transients"
REMOTE_HOST = "voevent.dc3.com"
REMOTE_PORT = 8099
ZMQ_HOST = "*"
ZMQ_PORT = 8089
ALIVE_ROLES = ("iamalive")
VOEVENT_ROLES = ('observation', 'prediction', 'utility', 'test')

# Simple VOEvent listener.
# John Swinbank, <swinbank@transientskp.org>, 2011.

# Quick & dirty configuration.
LOCAL_IVO = "ivo://lofar/transients"
REMOTE_HOST = "voevent.dc3.com"
REMOTE_PORT = 8099
ZMQ_HOST = "*"
ZMQ_PORT = 8089
ALIVE_ROLES = ("iamalive")
VOEVENT_ROLES = ('observation', 'prediction', 'utility', 'test')

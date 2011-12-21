# Simple VOEvent-ZeroMQ client.
# John Swinbank, <swinbank@transientskp.org>, 2011.
import zmq

ZMQ_HOST = "voevent.transientskp.org"
ZMQ_PORT = 8089

if __name__ == "__main__":
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://%s:%d" % (ZMQ_HOST, ZMQ_PORT))
    socket.setsockopt(zmq.SUBSCRIBE, "")

    while True:
        print socket.recv()

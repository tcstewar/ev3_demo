import time
import socket
import nengo
import thread

import numpy as np

class UDP(object):
    def __init__(self, size_in, size_out, address, in_port=None, out_port=None, period=0.1):
        self.target = (address, out_port)
        self.period = period
        self.size_in = size_in
        self.size_out = size_out
        self.data = [0] * size_out
        self.last_time = None
        if out_port is not None:
            self.socket_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_out.settimeout(None)
        if in_port is not None:
            self.socket_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_in.bind(('127.0.0.1', in_port))
            self.socket_in.settimeout(None)
            thread.start_new_thread(self.receiver, ())

    def receiver(self):
        while True:
            data = self.socket_in.recv(2048)

            data = data.strip().split(',')

            self.data = [float(xx) for xx in data]



    def __call__(self, t, *args):
        if self.size_in > 0:
            now = time.time()
            if self.last_time is None or now > self.last_time + self.period:
                msg = ','.join(['%g' % xx for xx in args[0]])

                print 'sending', t, msg

                self.socket_out.sendto(msg, self.target)
                self.last_time = now

        return self.data


if __name__ == '__main__':
    model = nengo.Network()
    with model:
        node1 = nengo.Node(UDP(size_in=1, size_out=0, address='localhost', out_port=8888), size_in=1, size_out=0)
        node2 = nengo.Node(UDP(size_in=0, size_out=1, address='localhost', in_port=8888), size_in=0, size_out=1)

        stimulus = nengo.Node(np.sin)
        nengo.Connection(stimulus, node1, synapse=None)

    sim = nengo.Simulator(model)
    while True:
        sim.run(1, progress_bar=False)



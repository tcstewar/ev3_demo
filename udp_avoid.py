import nengo
import nstbot
import numpy as np

import time

import udp

synapse = 0.01

model = nengo.Network(label='EV3 Demo Avoidance System')
with model:
    udp_node = nengo.Node(udp.UDP(size_in=4, size_out=4, address='localhost',
                                  in_port=8888, out_port=8889),
                          size_in=4, size_out=4)

    sensors_ir = nengo.Ensemble(n_neurons=200, dimensions=2)
    nengo.Connection(udp_node[[1, 2]], sensors_ir, synapse=None)
    def avoid_spin(x):
        turn_speed = max(x[0], x[1]) * 0.4
        if x[0] > x[1]:
            turn_speed *= -1
        return turn_speed
    nengo.Connection(sensors_ir, udp_node[2], synapse=synapse,
                     function=avoid_spin)

    def avoid_backup(x):
        close = (x[0] + x[1]) / 2
        speed = (close - 0.5) * 0.5
        if speed < 0:
            speed = 0
        return -speed
    nengo.Connection(sensors_ir, udp_node[1], synapse=synapse,
                     function=avoid_backup)

    sensors_us = nengo.Ensemble(n_neurons=200, dimensions=2, label='Sensors (US)')
    nengo.Connection(udp_node[[0, 3]], sensors_us, synapse=None)
    def avoid_dodge(x):
        dodge = 0
        dodge -= max(x[0] - 0.5, 0) * 1
        dodge += max(x[1] - 0.5, 0) * 1
        return dodge
    nengo.Connection(sensors_us, udp_node[0], synapse=synapse,
                     function=avoid_dodge)


if False:
    import nengo_viz
    viz = nengo_viz.Viz(model)
    viz.value(sensors_ir)
    viz.value(sensors_us)
    viz.slider(udp_node)
    viz.start()
else:
    sim = nengo.Simulator(model)
    while True:
        sim.run(1, progress_bar=None)



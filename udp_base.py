import nengo
from nengo.dists import Uniform
import nstbot
import numpy as np

import joystick_node
import udp
import time

use_bot = False

if use_bot:
    bot = nstbot.EV3Bot()
    #bot.connect(nstbot.connection.Socket('192.168.1.160'))
    bot.connect(nstbot.connection.Socket('10.162.177.187'))
    time.sleep(1)
    bot.connection.send('!M+\n')
    bot.activate_sensor([1, 2, 3, 4], period=0.05)

synapse = 0.006
msg_period = 0.1

model = nengo.Network(label='EV3 Demo')
with model:
    joystick = nengo.Node([0,0,0,0,0,0])#joystick_node.Joystick())

    control = nengo.networks.EnsembleArray(n_ensembles = 4, n_neurons=100)
    nengo.Connection(joystick[:4], control.input, synapse=None)

    motor = nengo.networks.EnsembleArray(n_ensembles = 4, n_neurons=100)
    for ens in motor.ensembles:
        ens.intercepts = Uniform(0.05, 0.9)



    omni_transform = np.array([[-1, 0, -1], [0.5, 1, -0.5], [1, -1, -1]]).T
    nengo.Connection(control.output[[1, 0, 2]], motor.input[:3],
                     transform=omni_transform * 2, synapse=synapse)
    nengo.Connection(control.output[3], motor.input[3], transform=-1,
                     synapse=synapse)


    def bot_motor(t, x):
        if use_bot:
            bot.motor(1, x[0], msg_period=msg_period)
            bot.motor(0, x[1], msg_period=msg_period)
            bot.motor(2, x[2], msg_period=msg_period)
            if abs(x[3]) > 0:
                bot.motor(3, x[3]*0.2, msg_period=msg_period)
            else:
                bot.motor(3, 0, msg_period=msg_period)
    motor_node = nengo.Node(bot_motor, size_in=4)
    nengo.Connection(motor.output, motor_node, synapse=synapse)

    def sensors(t):
        #left = (bot.lego_sensors[0] + bot.lego_sensors[1]) * 0.5
        #right = (bot.lego_sensors[2] + bot.lego_sensors[3]) * 0.5
        #joystick.output.joystick.set_vibration(left, right)

        if use_bot:
            return bot.lego_sensors
        else:
            return [0, 0, 0, 0]
    sensor_node = nengo.Node(sensors, size_out=4)


    udp_node = nengo.Node(udp.UDP(size_in=4, size_out=4, address='localhost',
                                  in_port=8889, out_port=8888),
                          size_in=4, size_out=4)

    nengo.Connection(sensor_node, udp_node, synapse=None)
    nengo.Connection(udp_node, control.input, synapse=synapse)

    '''
    avoid_inhibit = nengo.Ensemble(n_neurons=50, dimensions=1,
                                   intercepts=Uniform(0.2, 0.9))
    nengo.Connection(joystick[5], avoid_inhibit, synapse=None)
    nengo.Connection(avoid_inhibit, sensors_ir.neurons, transform=[[-1]]*200,
                     synapse=0.1)
    nengo.Connection(avoid_inhibit, sensors_us.neurons, transform=[[-1]]*200,
                     synapse=0.1)
    '''

if True:
    import nengo_viz
    viz = nengo_viz.Viz(model)
    viz.slider(sensor_node)
    viz.value(control.output)
    viz.value(motor.output)
    viz.raster(motor.ensembles[0].neurons, n_neurons=50)
    viz.raster(control.ensembles[0].neurons, n_neurons=10)
    viz.start()



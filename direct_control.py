import nengo
import nstbot
import numpy as np

import joystick_node
import time

bot = nstbot.EV3Bot()
bot.connect(nstbot.connection.Socket('192.168.1.160'))
#bot.connect(nstbot.connection.Socket('10.162.177.187'))
time.sleep(1)
bot.connection.send('!M+\n')
bot.activate_sensor([1, 2, 3, 4], period=0.05)

model = nengo.Network()
with model:
    joystick = nengo.Node(joystick_node.Joystick())

    def motor(t, x):
        bot.motor(1, x[0], msg_period=0.1)
        bot.motor(0, x[1], msg_period=0.1)
        bot.motor(2, x[2], msg_period=0.1)
        bot.motor(3, x[3], msg_period=0.1)
    motor_node = nengo.Node(motor, size_in=4)

    transform = np.array([[-1, 0, -1], [0.5, 1, -0.5], [1, -1, -1]]).T
    nengo.Connection(joystick[[1,0,2]], motor_node[:3],
                     transform=transform*2, synapse=None)
    nengo.Connection(joystick[3], motor_node[3], transform=-0.1, synapse=None)

    def sensors(t):
        left = (bot.lego_sensors[0] + bot.lego_sensors[1]) * 0.5
        right = (bot.lego_sensors[2] + bot.lego_sensors[3]) * 0.5
        #joystick.output.joystick.set_vibration(left, right)

        return bot.lego_sensors
    sensor_node = nengo.Node(sensors, size_out=4)

    #for i in range(10):
    #    ens = nengo.Ensemble(n_neurons=500, dimensions=4)
    #    nengo.Connection(sensor_node, ens, synapse=None)


import nengo_viz
viz = nengo_viz.Viz(model)
viz.value(sensor_node)
viz.value(joystick)
viz.start()

#sim = nengo.Simulator(model)
#while True:
#    sim.run(1, progress_bar=None)



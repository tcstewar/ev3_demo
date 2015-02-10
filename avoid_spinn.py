import nengo
import nstbot
import numpy as np

import joystick_node
import time

bot = nstbot.EV3Bot()
#bot.connect(nstbot.connection.Socket('192.168.1.160'))
bot.connect(nstbot.connection.Socket('10.162.177.187'))
time.sleep(1)
bot.connection.send('!M+\n')
bot.activate_sensor([1, 2, 3, 4], period=0.05)

synapse = 0.01

model = nengo.Network()
with model:
    joystick = nengo.Node(joystick_node.Joystick())

    control = nengo.networks.EnsembleArray(n_ensembles = 4, n_neurons=100)
    nengo.Connection(joystick[:4], control.input, synapse=None)

    #dz_cfg = nengo.Config(nengo.Ensemble)
    #dz_cfg[nengo.Ensemble].intercepts = nengo.dists.Uniform(0.05, 0.9)
    #with dz_cfg:
    motor = nengo.networks.EnsembleArray(n_ensembles = 4, n_neurons=100)

    omni_transform = np.array([[-1, 0, -1], [0.5, 1, -0.5], [1, -1, -1]]).T
    nengo.Connection(control.output[[1, 0, 2]], motor.input[:3],
                     transform=omni_transform * 2, synapse=synapse)
    nengo.Connection(control.output[3], motor.input[3], transform=-1,
                     synapse=synapse)

    def bot_motor(t, x):
        bot.motor(1, x[0], msg_period=0.2)
        bot.motor(0, x[1], msg_period=0.2)
        bot.motor(2, x[2], msg_period=0.2)
        bot.motor(3, x[3]*0.1, msg_period=0.2)
    motor_node = nengo.Node(bot_motor, size_in=4)
    nengo.Connection(motor.output, motor_node, synapse=synapse)

    '''

    def sensors(t):
        left = (bot.lego_sensors[0] + bot.lego_sensors[1]) * 0.5
        right = (bot.lego_sensors[2] + bot.lego_sensors[3]) * 0.5
        #joystick.output.joystick.set_vibration(left, right)

        return bot.lego_sensors
    sensor_node = nengo.Node(sensors, size_out=4)

    sensors_ir = nengo.Ensemble(n_neurons=200, dimensions=2)
    nengo.Connection(sensor_node[[1, 2]], sensors_ir, synapse=None)
    def avoid_spin(x):
        turn_speed = max(x[0], x[1]) * 0.4
        if x[0] > x[1]:
            turn_speed *= -1
        return turn_speed
    nengo.Connection(sensors_ir, control.input[2], synapse=synapse,
                     function=avoid_spin)

    def avoid_backup(x):
        close = (x[0] + x[1]) / 2
        speed = (close - 0.5) * 0.5
        if speed < 0:
            speed = 0
        return -speed
    nengo.Connection(sensors_ir, control.input[1], synapse=synapse,
                     function=avoid_backup)

    sensors_us = nengo.Ensemble(n_neurons=200, dimensions=2)
    nengo.Connection(sensor_node[[0, 3]], sensors_us, synapse=None)
    def avoid_dodge(x):
        dodge = 0
        dodge -= max(x[0] - 0.5, 0) * 1
        dodge += max(x[1] - 0.5, 0) * 1
        return dodge
    nengo.Connection(sensors_us, control.input[0], synapse=synapse,
                     function=avoid_dodge)


    avoid_inhibit = nengo.Ensemble(n_neurons=50, dimensions=1,
                                   intercepts=nengo.utils.distributions.Uniform(0.2, 0.9))
    nengo.Connection(joystick[5], avoid_inhibit, synapse=None)
    nengo.Connection(avoid_inhibit, sensors_ir.neurons, transform=[[-1]]*200,
                     synapse=0.1)
    nengo.Connection(avoid_inhibit, sensors_us.neurons, transform=[[-1]]*200,
                     synapse=0.1)
    '''

import nengo_spinnaker
sim = nengo_spinnaker.Simulator(model)
sim.run(1000)

'''
import nengo_viz
viz = nengo_viz.Viz(model)
viz.value(sensor_node)
viz.value(control.output)
viz.value(motor.output)
viz.start()
'''
#sim = nengo.Simulator(model)
#while True:
#    sim.run(1, progress_bar=None)



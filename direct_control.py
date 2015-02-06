import nengo
import nstbot
import numpy as np

import joystick_node
import time

bot = nstbot.EV3Bot()
bot.connect(nstbot.connection.Socket('192.168.1.160'))
time.sleep(1)
bot.connection.send('!M+\n')
bot.retina(True)
bot.show_image()

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
                     transform=transform*2, synapse=0.1)
    nengo.Connection(joystick[3], motor_node[3], transform=0.1)

sim = nengo.Simulator(model)
while True:
    sim.run(1, progress_bar=None)



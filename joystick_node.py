import nengo

import xinput

class Joystick(object):
    def __init__(self, index=0, verbose=False):
        joysticks = xinput.XInputJoystick.enumerate_devices()
        self.joystick = joysticks[index]
        self.verbose = verbose
        self.axis = dict(r_thumb_x=0, r_thumb_y=0,
                         l_thumb_x=0, l_thumb_y=0)
        self.buttons = {}
        self.size_out = 4

        @self.joystick.event
        def on_button(button, pressed):
            self.buttons[button] = pressed
            if verbose:
                print('button', button, pressed)

        @self.joystick.event
        def on_axis(axis, value):
            self.axis[axis] = value
            if verbose:
                print('axis', axis, value)

        @self.joystick.event
        def on_missed_packet(number):
            print('missed %(number)d packets' % vars())

    def __call__(self, t):
        self.joystick.dispatch_events()
        return [self.axis['l_thumb_x'], self.axis['l_thumb_y'],
                self.axis['r_thumb_x'], self.axis['r_thumb_y']]


if __name__ == '__main__':
    model = nengo.Network()
    with model:
        node = nengo.Node(Joystick())
        left = nengo.Ensemble(n_neurons=200, dimensions=2)
        right = nengo.Ensemble(n_neurons=200, dimensions=2)
        nengo.Connection(node[:2], left, synapse=None)
        nengo.Connection(node[2:4], right, synapse=None)


    import nengo_viz
    viz = nengo_viz.Viz(model)
    viz.value(left)
    viz.value(right)
    viz.start()

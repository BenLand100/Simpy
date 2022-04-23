#/usr/bin/python3

import simpy.library.io as io
from simpy.library.global_vals import *

import numpy as np

if __name__ == '__main__':
    print('Client dimensions:')
    print(f'  client_x:{client_x} client_y:{client_y} client_w:{client_w} client_h:{client_h}')
    print('Moving the mouse for a bit')
    for i in range(10):
        x = np.random.randint(client_x,client_w)
        y = np.random.randint(client_y,client_h)
        io.wind_mouse(x,y)
    
#! /usr/bin/python3

import numpy as np

class Environment():

    def __init__(self, ss, grid_num):
        self.ss = ss
        self.grid_num = grid_num
        self.x_coords = np.arange(0, self.grid_num, dtype=float)

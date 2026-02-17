#! /usr/bin/python3

import numpy as np

class Environment():

    def __init__(self, ss, grid_num, seed):
        self.ss = ss
        self.grid_num = grid_num
        self.x_coords = np.arange(0, self.grid_num, dtype=float)
        self.obstacles = self.generate_random_obstacles(0.1)

    def generate_random_obstacles(self, density):
        rng = np.random.default_rng()
        obstacles = np.full(self.grid_num**2, 0)
        for i in range(len(obstacles)):
            if rng.random() < density:
                obstacles[i] = 1
        return np.reshape(obstacles, (self.grid_num, self.grid_num))

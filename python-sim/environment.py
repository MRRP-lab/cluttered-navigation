#! /usr/bin/python3

import numpy as np

class Environment():

    def __init__(self, ss, grid_num, seed, startLine, finishLine):
        self.ss = ss
        self.grid_num = grid_num
        self.x_coords = np.arange(0, self.grid_num, dtype=float)
        self.seed = seed
        self.obstacles = self.generate_random_obstacles(0.1)

        self.startLine = startLine
        self.finishLine = finishLine

    def generate_random_obstacles(self, density):
        rng = np.random.default_rng(self.seed)
        obstacles = np.full(self.grid_num**2, 0)
        for i in range(len(obstacles)):
            if rng.random() < density:
                obstacles[i] = 1
        return np.reshape(obstacles, (self.grid_num, self.grid_num))

    def is_obstacle(self, x, y):
        if (x >= self.obstacles.shape[0] or x < 0):
            return 0
        if (y >= self.obstacles.shape[1] or y < 0):
            return 0
        return self.obstacles[y, x]
    
    def is_startLine(self, x, y):
        return (x == self.startLine)
    
    def is_finishLine(self, x, y):
        return (x == self.finishLine)

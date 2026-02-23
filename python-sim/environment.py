#! /usr/bin/python3

import numpy as np

class Environment():

    def __init__(self, ss, grid_num, seed):
        self.ss = ss
        self.grid_num = grid_num
        self.x_coords = np.arange(0, self.grid_num, dtype=float)
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.obstacles = self.generate_plinko_grid(5, 5, 2, 1)
        # self.obstacles = self.generate_random_obstacles(0.1)

    def generate_random_obstacles(self, density):
        obstacles = np.full(self.grid_num**2, 0)
        for i in range(len(obstacles)):
            if self.rng.random() < density:
                obstacles[i] = 1
        return np.reshape(obstacles, (self.grid_num, self.grid_num))

    # noise is how far an obstacle can move from its original position
    def generate_plinko_grid(self, start_col, row_gap, pin_gap, noise):
        obstacles = np.full(self.grid_num**2, 0)
        obstacles = np.reshape(obstacles, (self.grid_num, self.grid_num))
        col = start_col
        offset = 0
        while col < obstacles.shape[0]:
            if col % (row_gap + 1) != 0:
                col += 1
                continue
            for row in range(obstacles.shape[1]):
                if (row + offset) % (pin_gap + 1) != 0:
                    continue

                x_noise = self.rng.integers(-noise, noise, endpoint=True)
                y_noise = self.rng.integers(-noise, noise, endpoint=True)
                self.set_obstacle(col + x_noise, row + y_noise, 1, obstacles)
            col += 1
            offset = (offset + 1) % (pin_gap + 1)
        return obstacles

    def is_obstacle(self, x, y):
        if (x >= self.obstacles.shape[0] or x < 0):
            return 0
        if (y >= self.obstacles.shape[1] or y < 0):
            return 1
        return self.obstacles[y, x]

    # Use this function which handles out of bounds coordinates gracefully
    def set_obstacle(self, x, y, value, obstacles):
        if (x >= obstacles.shape[0] or x < 0):
            return
        if (y >= obstacles.shape[1] or y < 0):
            return
        obstacles[y, x] = value

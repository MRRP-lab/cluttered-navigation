#! /usr/bin/python3

import numpy as np
import math


class Environment():
    def __init__(self, ss, grid_num, seed):
        self.ss = ss
        self.grid_num = grid_num
        self.x_coords = np.arange(0, self.grid_num, dtype=float)
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.obstacles = self.generate_plinko_grid(5, 5, 1, 1)
        self.add_reflecting_boundary(self.obstacles, math.pi / 8, 20)

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
                x = col + x_noise
                y = row + y_noise

                if (x < obstacles.shape[0] and x >= 0 and
                    y < obstacles.shape[1] and y >= 0):
                    obstacles[y, x] = 1
            col += 1
            offset = (offset + 1) % (pin_gap + 1)
        return obstacles

    def add_reflecting_boundary(self, obstacles, angle, x_offset):
        line_length = 200
        x0 = obstacles.shape[0] + x_offset
        y0 = round(obstacles.shape[1] / 2)
        x1 = round(x0 - line_length * math.cos(angle)) + x_offset
        y1_neg = round(y0 - line_length * math.sin(angle))
        y1_pos = round(y0 + line_length * math.sin(angle))

        self.add_rasterized_obstacle_line(obstacles, x0, y0, x1, y1_neg)
        self.add_rasterized_obstacle_line(obstacles, x0, y0, x1, y1_pos)

    # Rasterize some lines into grid cells.
    # Right now, it casts the lines from a point starting in the middle
    # of the right side of the screen. Each line is angle degrees off of
    # the horizontal, with a total angle between equal to 2*angle.
    # We implement Bresenham's line algorithm from computer graphics for
    # rasterizing a line.
    def add_rasterized_obstacle_line(self, obstacles, x0, y0, x1, y1):
        def plot_line_low(x0, y0, x1, y1):
            dx = x1 - x0
            dy = y1 - y0
            yi = 1
            if dy < 0:
                yi = -1
                dy = -dy
            D = (2 * dy) - dx
            y = y0
            for x in range(x0, x1):
                self.set_obstacle(obstacles, x, y, 1)
                if D > 0:
                    y += yi
                    D += 2 * (dy - dx)
                else:
                    D += 2 * dy

        def plot_line_high(x0, y0, x1, y1):
            dx = x1 - x0
            dy = y1 - y0
            xi = 1
            if dx < 0:
                xi = -1
                dx = -dx
            D = (2 * dx) - dy
            x = x0
            for y in range(y0, y1):
                self.set_obstacle(obstacles, x, y, 1)
                if D > 0:
                    x += xi
                    D += 2 * (dx - dy)
                else:
                    D += 2 * dx

        if abs(y1 - y0) < abs(x1 - x0):
            if x0 > x1:
                plot_line_low(x1, y1, x0, y0)
            else:
                plot_line_low(x0, y0, x1, y1)
        else:
            if y0 > y1:
                plot_line_high(x1, y1, x0, y0)
            else:
                plot_line_high(x0, y0, x1, y1)

    def is_obstacle(self, x, y):
        if (x >= self.obstacles.shape[0] or x < 0):
            return 0
        if (y >= self.obstacles.shape[1] or y < 0):
            return 1
        return self.obstacles[y, x]

    # Set obstacles using this function which ensures safety.
    def set_obstacle(self, obstacles, x, y, value):
        if (x < obstacles.shape[0] and x >= 0
           and (y < obstacles.shape[1] and y >= 0)):
            obstacles[y, x] = value

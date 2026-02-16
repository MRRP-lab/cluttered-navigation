#! /usr/bin/python3
#
import numpy as np


class Environment():

    def __init__(self, ss, grid_num):
        self.ss = ss
        self.grid_num = grid_num
        self.x_coords = np.arange(0, self.grid_num, dtype=float)
        self.new_grid = np.arange(0, self.grid_num*self.grid_num, dtype=tuple)

    # Stigmergy utils
    #####################################################################################
    #Creates array of tuples (x, y, index, stimulus) to represent the corners of the grid
    #and sets "new_grid" equal to the array and returns the array
    def make_grid(self, grid_num):
        interval = self.ss/grid_num
        grid_corners = np.arange(0, grid_num*grid_num, dtype=tuple)
        index = 0

        for x_vals in range(grid_num):
            x = float(x_vals*interval)
            self.x_coords[x_vals] = float(x)
            for y_vals in range(grid_num):
                y = float(y_vals*interval)
                grid_corners[index] = (x, y, index, 0.0)
                index += 1
        new_grid = grid_corners.reshape(grid_num, grid_num)
        self.new_grid = new_grid

        return new_grid

    #Takes in the coordinate that the robot is at, and returns the corresponding number
    # to the box in the grid it is in
    def coord_near(self, grid_num, robotCoord):
        interval = self.ss/grid_num
        x_ind = 0
        y_ind = 0

        for x_coord in range(grid_num):
            if (robotCoord[0] >= self.new_grid[x_coord][0][0] and robotCoord[0] < self.new_grid[x_coord][0][0]+interval):
                x_ind = x_coord

        for y_coord in range(grid_num):
            if (robotCoord[1] >= self.new_grid[x_ind][y_coord][1] and robotCoord[1] < self.new_grid[x_ind][y_coord][1]+interval):
                y_ind = y_coord

        box = (y_ind*grid_num)+x_ind
        return box

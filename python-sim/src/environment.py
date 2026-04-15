#! /usr/bin/python3

import numpy as np
import math
import itertools

class Environment():
    def __init__(self, grid_num, seed, boundary, boundary_angle, boundary_offset, row_gap, pin_gap, noise):
        self.grid_num = grid_num
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.obstacles = self.generate_plinko_grid(1, row_gap, pin_gap, noise)
        self.boundary = boundary
        self.boundary_offset = boundary_offset
        if self.boundary:
            self.add_reflecting_boundary(self.obstacles, math.radians(boundary_angle), self.boundary_offset)

        self.start_line = 0
        self.finish_line = self.grid_num

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
                #x_noise = round(self.rng.normal(0, noise))
                #y_noise = round(self.rng.normal(0, noise))
                x = col + x_noise
                y = row + y_noise

                if (x < obstacles.shape[0] and x >= 0 and
                    y < obstacles.shape[1] and y >= 0):
                    obstacles[y, x] = 1
            col += 1
            offset = (offset + 1) % (pin_gap + 1)
        return obstacles

    def add_reflecting_boundary(self, obstacles, angle, y_offset):
        # max possible just to make sure our boundary gets to the end
        line_length = self.grid_num * math.sqrt(2)
        center_y = math.floor(self.grid_num / 2)
        start_x = 0
        end_x = round(line_length * math.cos(angle))

        # top and bottom visually
        top_y0 = round(center_y - y_offset)
        top_y1 = round(top_y0 - line_length * math.sin(angle))

        bot_y0 = round(center_y + y_offset)
        bot_y1 = round(bot_y0 + line_length * math.sin(angle))
        self.add_rasterized_obstacle_line(obstacles, start_x, top_y0, end_x, top_y1)
        self.add_rasterized_obstacle_line(obstacles, start_x, bot_y0, end_x, bot_y1)

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

    # strict_bounds overrides edge behavior of the obstacle grid.
    def is_obstacle(self, x, y, strict_bounds=False):
        # Extend straight lines out of the ends of the
        # boundary at the beginning
        if (self.boundary and x < 0 and not strict_bounds):
            if abs(y - round(self.grid_num / 2)) < self.boundary_offset:
                return 0
            else:
                return 1
        if (x >= self.obstacles.shape[0] or x < 0):
            if strict_bounds: return 1
            return 0
        if (y >= self.obstacles.shape[1] or y < 0):
            if strict_bounds: return 1
            return 1
        return self.obstacles[y, x]

    # Set obstacles using this function which ensures safety.
    def set_obstacle(self, obstacles, x, y, value):
        if (x < obstacles.shape[0] and x >= 0
           and (y < obstacles.shape[1] and y >= 0)):
            obstacles[y, x] = value

    # The java server doesn't allow two robots to occupy the same space,
    # and enforces the fact that robots can only have one goal node.
    # So we modify the graph with super sinks to allow the robots to cross
    # the finish line anywhere.
    def to_adj_matrix_with_supersinks(self, super_sinks):
        # Flood fill from center left node
        center_y = math.ceil(self.grid_num / 2)
        first_node = Node(0, center_y)
        remaining_nodes = [first_node]
        adj_list = {}
        visited = {(first_node.x, first_node.y)}

        while len(remaining_nodes) > 0:
            current = remaining_nodes.pop()
            adj_list[(current.x, current.y)] = current
            neighbors = current.get_euclidean_neighbor_coords()

            for neighbor in neighbors:
                if (self.is_obstacle(neighbor[0], neighbor[1], strict_bounds=True)):
                    continue
                if neighbor in visited:
                    if neighbor in adj_list:
                        current.add_neighbor(adj_list[neighbor])
                        adj_list[neighbor].add_neighbor(current)
                    continue

                visited.add(neighbor)
                new_node = Node(neighbor[0], neighbor[1])
                current.add_neighbor(new_node)
                new_node.add_neighbor(current)
                adj_list[neighbor] = new_node
                remaining_nodes.append(new_node)

        # Add starting area square behind x=0
        # first populate with nodes then create edges
        for x in range(-2 * self.boundary_offset, 0):
            # range excludes the end so add one
            for y in range(-self.boundary_offset, self.boundary_offset):
                adj_list[(x, y + center_y)] = Node(x, y + center_y)

        for node in adj_list.values():
            neighbors = node.get_euclidean_neighbor_coords()
            for neighbor in neighbors:
                neighbor = adj_list.get(neighbor)
                if (neighbor is not None):
                    node.add_neighbor(neighbor)
                    neighbor.add_neighbor(node)

        # Add super sinks which don't have coordinates.
        sinks = [Node(None, None) for _ in range(super_sinks)]

        for y in range(self.grid_num):
            node = adj_list.get((self.grid_num-1, y))
            if node is not None:
                for sink in sinks:
                    node.add_neighbor(sink)
        return adj_list, sinks

# Used to aid adjacency list representation.
class Node:
    id = itertools.count()
    def __init__(self, x, y):
        self.id = next(Node.id)
        self.x = x
        self.y = y
        self.neighbors = []
    
    def add_neighbor(self, node):
        self.neighbors.append(node)

    def get_euclidean_neighbor_coords(self):
        return [(self.x,   self.y+1),
                (self.x,   self.y-1),
                (self.x+1, self.y),
                (self.x-1, self.y)]

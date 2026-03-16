import numpy as np
from enum import Enum
import math
import heapq
import itertools

class PlinkoState(Enum):
    RIGHT = 0
    UP = 1
    DOWN = 2
    TRAPPED = 3

class Robots():
    def __init__(self, N, spawn, density, seed):
        #TODO separate env from robot, set env separately. Make boundary a function call to add it.
        self.env = None
        self.num = N
        self.rng = np.random.default_rng(seed)
        coords = np.full(self.num * 2, 0)
        self.coords = np.reshape(coords, (self.num, 2))

        # We can't give our robots an actual location until we know where the start line is.
        self.spawn_radius, self.offsets = self.generate_circular_spawn_offsets(density)
        # TODO: Separate navigation logic for each different strategy
        # to a different place.
        self.plinko_state = np.full(self.num, PlinkoState.RIGHT)

        # For crowd compression reasons, keep robots such that
        # we can update the rightmost ones first.
        self.re_sort_rightmost()

    # it gets a function in case there are special things we need to do
    def set_environment(self, env):
        self.env = env
        self.spawn_before_start_line(self.spawn_radius, self.offsets)

    # Spawn robots in a circular manner around a point such that no robots are overlapping.
    def generate_circular_spawn_offsets(self, density):
        tiebreaker = itertools.count()

        square_r = 1
        r = 1
        spawned = 0
        points = [(0, next(tiebreaker), np.array([0, 0]))]
        raw_offsets = []

        # Dynamically keep track of the furthest extent so we can adjust the X coordinates
        # to behind the starting line.
        max_radius = 0
        while spawned < self.num:
            offsets = []
            for offset in range(-square_r, square_r+1):
                offsets.append(np.array([offset, square_r])) # Top
                offsets.append(np.array([offset, -square_r])) # Bottom

            for offset in range(-square_r+1, square_r):
                offsets.append(np.array([square_r, offset])) # Right
                offsets.append(np.array([-square_r, offset])) # Left

            new_entries = []
            for rel_pos in offsets:
                new_entries.append((np.linalg.norm(rel_pos), next(tiebreaker), rel_pos))

            points.extend(new_entries)
            heapq.heapify(points)
            square_r += 1

            while (spawned < self.num and len(points) > 0 and
                   points[0][0] < r and points[0][0] >= r-1):
                nearest = heapq.heappop(points)
                if (self.rng.random() < density):
                    if nearest[0] > max_radius:
                        max_radius = nearest[0]
                    raw_offsets.append(nearest[2])
                    spawned += 1
            r += 1
            # While the heap is not empty and the min element is within the current ring,
            # pop it and place a robot there. Stop when no more bots to place.
        return max_radius, np.array(raw_offsets)

    # Move behind the start line
    def spawn_before_start_line(self, furthest_extent, offsets):
        start_line = self.env.start_line
        map_height = self.env.grid_num
        center = np.array([math.floor(-furthest_extent) + start_line,  math.floor(map_height / 2)])
        for r in range(self.num):
            self.coords[r] = offsets[r] + center

    def re_sort_rightmost(self):
        self.rightmost_sorted_robots = sorted(range(self.num), reverse=True,
                                              key=lambda i: self.coords[i, 0])

    # Drives movement updates for robots in their environment.
    # Update robots from the right to left side of the screen.
    def update_movement(self):
        for r in range(self.num):
            self.plinko_movement_policy(r)

    # Move right. At an obstacle, randomly choose either up or down.
    # TODO: Separate navigation strategy logic out of Robots.
    def plinko_movement_policy(self, r):
        c = self.coords[r]
        xnew = c[0]
        ynew = c[1]

        right = self.env.is_obstacle(c[0]+1, c[1]) +\
            self.is_robot(c[0]+1, c[1])

        up = self.env.is_obstacle(c[0], c[1]-1) +\
            self.is_robot(c[0], c[1]-1)

        down = self.env.is_obstacle(c[0], c[1]+1) +\
            self.is_robot(c[0], c[1]+1)

        state = self.plinko_state[r]
        new_state = None

        if right == 0:
            new_state = PlinkoState.RIGHT
        elif (up == 0 and down == 0):
            if (state == PlinkoState.RIGHT or state == PlinkoState.TRAPPED):
                if (self.rng.random() < 0.5):
                    new_state = PlinkoState.DOWN
                else:
                    new_state = PlinkoState.UP
            else:
                new_state = state
        elif (up == 0):
            new_state = PlinkoState.UP
        elif (down == 0):
            new_state = PlinkoState.DOWN
        else:
            new_state = PlinkoState.TRAPPED

        self.plinko_state[r] = new_state

        match new_state:
            case PlinkoState.RIGHT:
                xnew += 1
            case PlinkoState.UP:
                ynew -= 1
            case PlinkoState.DOWN:
                ynew += 1
            case PlinkoState.TRAPPED:
                pass

        self.coords[r] = np.array([xnew, ynew])


    # TODO better representation of robot coordinates could make this quicker
    # Returns true if there's a robot at this position
    def is_robot(self, x, y):
        for pos in self.coords:
            if (x == pos[0] and y == pos[1]):
                return 1
        return 0

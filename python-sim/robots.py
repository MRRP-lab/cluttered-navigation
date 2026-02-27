import numpy as np
from enum import Enum
import heapq
import itertools

import environment

class PlinkoState(Enum):
    RIGHT = 0
    UP = 1
    DOWN = 2
    TRAPPED = 3

class Robots():
    def __init__(self, N, vel, ss, gridnum, seed):

        self.env = environment.Environment(ss, gridnum, seed)
        self.num = N
        self.ss = ss
        self.rng = np.random.default_rng(seed)
        
        coords = np.full(self.num * 2, 0)
        self.coords = np.reshape(coords, (self.num, 2))

        self.spawn_robots_around_point(25, 25, 1)

        self.v = np.full(self.num, vel)

        # TODO: Separate navigation logic for each different strategy
        # to a different place.
        self.plinko_state = np.full(self.num, PlinkoState.RIGHT)

        # For crowd compression reasons, keep robots such that
        # we can update the rightmost ones first.
        self.re_sort_rightmost()

    # Spawn robots in a circular manner around a point such that no robots are overlapping.
    def spawn_robots_around_point(self, x, y, density):
        target_point = np.array([x, y])
        
        tiebreaker = itertools.count()

        square_r = 1
        r = 1
        spawned = 0
        points = [(0, next(tiebreaker), target_point)]
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
                abs_pos = rel_pos + target_point
                new_entries.append((np.linalg.norm(rel_pos), next(tiebreaker), abs_pos))

            points.extend(new_entries)
            heapq.heapify(points)
            square_r += 1

            while (spawned < self.num and len(points) > 0 and
                   points[0][0] < r and points[0][0] >= r-1):
                pos = heapq.heappop(points)[2]
                if (self.rng.random() < density):
                    self.coords[spawned] = pos
                    spawned += 1
            r += 1
            # While the heap is not empty and the min element is within the current ring,
            # pop it and place a robot there. Stop when no more bots to place.

    def re_sort_rightmost(self):
        self.rightmost_sorted_robots = sorted(range(self.num), reverse=True,
                                              key=lambda i: self.coords[i, 0])

    # Drives movement updates for robots in their environment.
    # Update robots from the right to left side of the screen.
    def update_movement(self):
        for k in range(self.num):
            r = self.rightmost_sorted_robots[k]
            self.plinko_movement_policy(r)

        self.re_sort_rightmost()
        #for r in range(self.num):
        #    self.plinko_movement_policy(r)

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
            if (state == PlinkoState.RIGHT):
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

        match self.plinko_state[r]:
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

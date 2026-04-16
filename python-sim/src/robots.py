import numpy as np
from enum import Enum

class PlinkoState(Enum):
    RIGHT = 0
    UP = 1
    DOWN = 2
    TRAPPED = 3

class Robots():
    def __init__(self, N, seed, spawns, disabled_collision):
        self.env = None
        self.num = N
        self.rng = np.random.default_rng(seed)
        self.coords = spawns
        self.disabled_collision = disabled_collision

        # TODO: Separate navigation logic for each different strategy
        # to a different place.
        self.plinko_state = np.full(self.num, PlinkoState.RIGHT)

        # For crowd compression reasons, keep robots such that
        # we can update the rightmost ones first.
        self.re_sort_rightmost()

    # it gets a function in case there are special things we need to do
    def set_environment(self, env):
        self.env = env


    def re_sort_rightmost(self):
        self.rightmost_sorted_robots = sorted(range(self.num), reverse=True,
                                              key=lambda i: self.coords[i, 0])

    # Drives movement updates for robots in their environment.
    # Update robots from the right to left side of the screen.
    # Returns true if any robot has made progress towards the goal.
    def update_movement(self):
        progress = False
        for k in range(self.num):
            r = self.rightmost_sorted_robots[k]
            progress |= self.plinko_movement_policy(r)

        # TODO really slow? With or without this, there is artifacting in robot dispersion.
        self.re_sort_rightmost()
        return progress

    # Move right. At an obstacle, randomly choose either up or down.
    # TODO: Separate navigation strategy logic out of Robots.
    # Returns True if made progress and hasn't passed the finish line.
    def plinko_movement_policy(self, r):
        c = self.coords[r]
        xnew = c[0]
        ynew = c[1]
        progress = False
        right = self.env.is_obstacle(c[0]+1, c[1])
        up = self.env.is_obstacle(c[0], c[1]-1)
        down = self.env.is_obstacle(c[0], c[1]+1)
        
        if (not self.disabled_collision):
            right += self.is_robot(c[0]+1, c[1])
            up += self.is_robot(c[0], c[1]-1)
            down += self.is_robot(c[0], c[1]+1)

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
                if xnew < self.env.finish_line:
                    progress = True
                xnew += 1
            case PlinkoState.UP:
                ynew -= 1
            case PlinkoState.DOWN:
                ynew += 1
            case PlinkoState.TRAPPED:
                pass

        self.coords[r] = np.array([xnew, ynew])

        return progress


    # TODO better representation of robot coordinates could make this quicker. Trade space for time type deal.
    # As it stands, if all robots are doing robot-robot collision detection,
    # the total cost per frame is O(3n^2) when it could be O(3n). (storing robot coords in a matrix would make access equal O(1)
    # Returns true if there's a robot at this position
    def is_robot(self, x, y):
        for pos in self.coords:
            if (x == pos[0] and y == pos[1]):
                return 1
        return 0
    
    # Returns a list of entries containing these entries for each robot:
    # [id, x, y]
    def get_coordinate_data(self):
        return [[i, self.coords[i, 0], self.coords[i, 1]] for i in range(self.num)]

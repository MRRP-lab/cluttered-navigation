from .navstrategy import NavStrategy
import numpy as np
from enum import Enum

class PlinkoState(Enum):
    RIGHT = 0
    UP = 1
    DOWN = 2
    TRAPPED = 3

class PlinkoStrategy(NavStrategy):

    def __init__(self, num, robots, env, seed, no_progress_timeout, disabled_collision):
        super().__init__(robots, env)

        self.disabled_collision = disabled_collision
        self.no_prog_timeout = no_progress_timeout
        self.num = num
        self.rng = np.random.default_rng(seed)

        self.time = 0
        self.plinko_state = np.full(self.num, PlinkoState.RIGHT)

        self.data = []

    def sort_rightmost(self):
        return sorted(range(self.num), reverse=True,
                      key=lambda i: self.robots.coords[i, 0])

    def run(self):
        no_progress = 0
        time = 0

        while no_progress < self.no_prog_timeout:
            progress = self.update_movement()
            if (not progress):
                no_progress += 1
            else:
                no_progress = 0

            coordinate_data = self.robots.get_coordinate_data()
            coordinate_data = [[time] + row for row in coordinate_data]
            self.data.extend(coordinate_data)
            time += 1


    # Drives movement updates for robots in their environment.
    # Update robots from the right to left side of the screen.
    # Returns true if any robot has made progress towards the goal.
    def update_movement(self):
        progress = False
        rightmost = self.sort_rightmost()
        for k in range(self.num):
            r = rightmost[k]
            progress |= self.plinko_movement_policy(r)

        return progress


    # Move right. At an obstacle, randomly choose either up or down.
    # Returns True if made progress and hasn't passed the finish line.
    def plinko_movement_policy(self, r):
        robots = self.robots
        
        c = robots.coords[r]
        xnew = c[0]
        ynew = c[1]
        progress = False

        right = self.env.is_obstacle(c[0]+1, c[1])
        up = self.env.is_obstacle(c[0], c[1]-1)
        down = self.env.is_obstacle(c[0], c[1]+1)

        if (not self.disabled_collision):
            right += robots.is_robot(c[0]+1, c[1])
            up += robots.is_robot(c[0], c[1]-1)
            down += robots.is_robot(c[0], c[1]+1)

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

        robots.coords[r] = np.array([xnew, ynew])

        return progress

    def extract_data(self):
        return self.data

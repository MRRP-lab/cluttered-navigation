from src.strategies.navstrategy import NavStrategy
import numpy as np
from enum import Enum


# Cardinal headings as (dx, dy) vectors. y grows downward here (matching
# how up/down are already used elsewhere in this codebase).
RIGHT = (1, 0)
DOWN = (0, 1)
LEFT = (-1, 0)
UP = (0, -1)


def _rotate_cw(d):
    """Rotate a heading 90 degrees clockwise (on-screen, y-down)."""
    return (-d[1], d[0])


def _rotate_ccw(d):
    """Rotate a heading 90 degrees counterclockwise (on-screen, y-down)."""
    return (d[1], -d[0])


def _reverse(d):
    return (-d[0], -d[1])


class Bug2Mode(Enum):
    GOAL_SEEK = 0    # walking the m-line towards the finish line
    WALL_FOLLOW = 1  # circumnavigating an obstacle


# Bug 2 is a bug algorithm for traversal with static obstacles in mind.
# Our simulation uses dynamic obstacles. Therefore, bug2 may not work exactly as theorized.

# Bugs using this algorithm do not traverse around randomly but rather deterministically,
# and they do it randomly
class Bug2(NavStrategy):
    def __init__(self, robots, env, no_progress_timeout):
        super().__init__(robots, env)
        self.no_prog_timeout = no_progress_timeout

        # FIX: self.num was used below (sort_rightmost, update_movement) but
        # never set anywhere in this class. robots.num is confirmed to exist
        # (optimal.py relies on it too), so using that.
        self.num = self.robots.num

        # Per-robot Bug2 memory. Every robot's goal is just "cross
        # x = finish_line", not a specific (x, y) point, so the m-line --
        # the line Bug2 always tries to walk towards the goal -- is simply
        # the horizontal row the robot started on. It's fixed for the
        # robot's whole run.
        self.mline_y = robots.coords[:, 1].copy()
        self.mode = [Bug2Mode.GOAL_SEEK] * self.num
        self.heading = [RIGHT] * self.num   # current wall-follow heading
        self.hit_x = [None] * self.num      # x where the m-line was last left

        self.data = []

    def run(self):
        no_progress = 0
        time = 0
        while no_progress < self.no_prog_timeout:
            progress = self.update_movement()
            if not progress:
                no_progress += 1
            else:
                no_progress = 0

            coordinate_data = self.robots.get_coordinate_data()
            coordinate_data = [[time] + row for row in coordinate_data]
            print(coordinate_data)
            self.data.extend(coordinate_data)
            time += 1

    def sort_rightmost(self):
        return sorted(range(self.num), reverse=True,
                      key=lambda i: self.robots.coords[i, 0])

    def update_movement(self):
        progress = False
        rightmost = self.sort_rightmost()
        for k in range(self.num):
            r = rightmost[k]
            progress |= self.bug2_movement_policy(r)

        return progress

    def _blocked(self, x, y):
        return self.env.is_obstacle(x, y) or self.robots.is_robot(x, y)

    # True Bug2: walk the m-line (the robot's starting row) towards the
    # goal. On hitting an obstacle, follow its boundary clockwise --
    # right-hand-on-the-wall -- remembering the x where the m-line was
    # left (the hit point). The moment the robot is back on the m-line
    # *and* past that hit point (the leave point), it drops wall-following
    # and resumes walking the m-line directly.
    #
    # The right-hand-rule turn order -- try turning right off your current
    # heading first, then straight, then left, then reverse -- is what
    # makes this real circumnavigation instead of a simple up/down dodge:
    # it traces the actual shape of any obstacle. It's also what gets a
    # robot out of a dead-end pocket for free: if right/straight/left are
    # all blocked, reverse is always still tried, so backing out of a trap
    # falls out of the same rule rather than needing special-case logic.
    def bug2_movement_policy(self, r):
        x, y = self.robots.coords[r]
        progress = False

        if self.mode[r] == Bug2Mode.GOAL_SEEK:
            if not self._blocked(x + 1, y) or x < 0:
                move = RIGHT
            else:
                # Hit the obstacle: remember where we left the m-line and
                # start hugging the wall.
                self.hit_x[r] = x
                self.mode[r] = Bug2Mode.WALL_FOLLOW
                move = self._wall_follow_move(x, y, RIGHT, first=True)
        else:
            move = self._wall_follow_move(x, y, self.heading[r])

        if move is None:
            return False  # boxed in on all four sides -- no legal move

        self.heading[r] = move
        nx, ny = x + move[0], y + move[1]
        self.robots.coords[r] = np.array([nx, ny])
        
        if move == RIGHT and x < self.env.finish_line:
            progress = True

        if (self.mode[r] == Bug2Mode.WALL_FOLLOW and
                #self.mline_y[r] and # This line right here enables/disables semi-circumnavigation
                nx > self.hit_x[r]):
            self.mode[r] = Bug2Mode.GOAL_SEEK

        return progress

    def _wall_follow_move(self, x, y, heading, first=False):
        """Right-hand rule: try turning right off `heading` first, then
        straight, then left, then reversing. Returns the first open
        direction, or None if all four are blocked.

        `first=True` is only for the single tick a robot first bumps into
        an obstacle. At that moment `heading` points straight at the wall,
        not alongside it, so there's no "right hand" contact established
        yet -- turning right first here would immediately head away from
        the wall it just hit. Turning left instead is what puts the wall
        on the robot's right hand, so every following tick's right-first
        search actually means something.
        """
        if first:
            order = (_rotate_ccw(heading), heading, _rotate_cw(heading), _reverse(heading))
        else:
            order = (_rotate_cw(heading), heading, _rotate_ccw(heading), _reverse(heading))
        for d in order:
            if not self._blocked(x + d[0], y + d[1]):
                return d
        return None

    def extract_data(self):
        return self.data

import itertools
import heapq
import numpy as np
import math

# Robot & Environment initialization relies on each other's parameters, so extract the negotiation logic here to reduce that circular dependency
# a little iffy on if this is good design or not
class SpawnLayout:
    def __init__(self, seed, num, robot_density, grid_num, start_line):
        self.num = num
        self.density = robot_density
        self.start_line = start_line
        self.grid_num = grid_num

        self.rng = np.random.default_rng(seed)

        self.max_radius, self.offsets = self.generate_circular_spawn_offsets(self.density)
        self.spawn_before_start_line()
        self.boundary_line_y_offset = self.max_radius

    # Move behind the start line
    def spawn_before_start_line(self):
        map_height = self.grid_num
        center = np.array([math.floor(-self.max_radius) + self.start_line,  math.ceil(map_height / 2)])
        for r in range(self.num):
            self.offsets[r] = self.offsets[r] + center

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
        return 1 + math.ceil(max_radius), np.array(raw_offsets)

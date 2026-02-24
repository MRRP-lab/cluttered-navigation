import numpy as np

import utils
import environment

class Robots():
    def __init__(self, N, vel, ss, gridnum, seed):

        # load basics
        self.env = environment.Environment(ss, gridnum, seed)
        self.num = N
        self.ss = ss

        # set up coordinates
        self.rng = np.random.default_rng(seed)
        coords = self.rng.choice(np.arange(gridnum), size=self.num*2)
        coords = np.reshape(coords, (self.num, 2))

        self.coords = np.array(coords, dtype=int)
        self.v = np.full(self.num, vel)

    def update_movement(self, r):
        c = self.coords[r]
        # cap value
        if (self.v[r] > 4):
            self.v[r] = 4
        elif (self.v[r] < 0):
            self.v[r] = 0

        xnew = c[0] + self.v[r]
        ynew = c[1]

        # update coords, no screen wrapping
        self.coords[r] = np.array([xnew, ynew])

    # Move right. At an obstacle, randomly choose either up or down.
    def plinko_movement_policy(self, r):
        c = self.coords[r]

        right = self.env.is_obstacle(c[0]+1, c[1])
        up = self.env.is_obstacle(c[0], c[1]-1)
        down = self.env.is_obstacle(c[0], c[1]+1)

        xnew = c[0]
        ynew = c[1]
        if right == 0:
            xnew += 1
        elif (up == 0 and down == 0):
            if (self.rng.random() < 0.5):
                ynew += 1
            else:
                ynew -= 1
        else:
            if (up == 0):
                ynew -= 1
            elif (down == 0):
                ynew += 1

        # update coords, no screen wrapping
        self.coords[r] = np.array([xnew, ynew])

    def distance_calc(self, diff, r, lim_distance):
        distances = np.linalg.norm(diff, axis=1)
        distances[r] = lim_distance
        valid_dist_ind = np.where(distances < lim_distance)
        # the value for the current robot doesn't matter
        # it is multiplied by 0 in the next steps
        distances[distances > lim_distance] = lim_distance
        # invert
        with np.errstate(divide='ignore'):
            inv_distances = 1-np.square(distances/lim_distance)

        inv_distances[inv_distances > 1] = 1
        return inv_distances, valid_dist_ind[0], distances

    # assume polygon obstacles do not have holes
    def check_collision_polygons(self, r, obstacles, prev_c):
        c = self.coords[r]
        loc_wrapped = utils.wrap_pt(c, self.ss, self.ss) # just in case? obstacle checking assumes we're in (0,ss)x(0,ss)

        # shoot ray back the way agent moved in last time step to both:
        # 1. check if we're inside obstacle
        # 2. and find which edge we collide with in case of collision
        ray_out = prev_c - c
        theta = np.arctan2(ray_out[1], ray_out[0])
        for o in obstacles: # list of CCW points
            inpoly = False
            # shoot one ray for each obstacle, then check edges individually if inside
            try:
                inpoly, data = utils.IsInPolyNoHoles(loc_wrapped, o, theta)
            except:
                # will raise exception if ray is parallel to polygon edge
                # TODO handle gracefully
                raise (ValueError, "in poly check not working")

            # if collision found, do billiard bounce
            if inpoly:
                closest_edge = data[0][1:]
                dist = 100000000
                # following check for closest edge not really necessary for our purposes
                # but ray may intersect multiple edges if obstacle nonconvex
                for pt, v1, v2 in data:
                    if np.linalg.norm(pt-c) < dist:
                        dist = np.linalg.norm(pt-c)
                        closest_edge = (v1, v2)
                        # reorient according to elastic collision law
                        theta = utils.bounce(closest_edge, prev_c, c)
                # move to previous location and rotate in place
                self.angles[r] = theta
                self.coords[r] = prev_c
                MADE_CHANGE = True
                break # assumes obstacles do not overlap
            else:
                pass

        return MADE_CHANGE

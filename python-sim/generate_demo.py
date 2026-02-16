import numpy as np
import random
import pandas as pd
import time
import os

# custom imports
import utils
from robots import *

########################## PARAMETERS ###########################################

#variables for saving data
sim_data = []
datadir = './data'
if not os.path.exists(datadir):
    os.mkdir(datadir)

# TODO: convert the below to be command-line arguments
FPS = 55
sim_time = 20
time_seconds = 20
sim_time = time_seconds*FPS
ss = 500  # screen size
N = 10
v = 1  # velocity
gridnum = 100

############################### MAIN ##############################################

### Load Configs

robots = Robots(N, v, ss, gridnum)

group_list = [np.zeros(robots.num)]

### Simulation Loop

for t in range(sim_time):

    big_coords, big_angles = utils.setup_big_arrays(robots)

    for r in range(robots.num):
        c = robots.coords[r].copy() # save previous position in case of collision
        # update robot positions
        robots.update_movement(r)

        # returns true if there was a collision
        # and moves robot back to original position and reorients


    sim_data.append([robots.coords[:,0].copy(), robots.coords[:,1].copy(), robots.angles.copy()])


data = pd.DataFrame(data = sim_data, columns = ["x","y","theta"])

outdat = os.path.join(datadir, "demo.csv")

data.to_csv(outdat, lineterminator = "")

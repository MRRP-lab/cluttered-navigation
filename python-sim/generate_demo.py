import numpy as np
import pandas as pd
import os

# custom imports
from robots import Robots
from params import Params


########################## PARAMETERS ###########################################

#variables for saving data
sim_data = []
datadir = './data'
if not os.path.exists(datadir):
    os.mkdir(datadir)

# TODO: convert the below to be command-line arguments
FPS = Params.FPS
time_seconds = Params.time_seconds
sim_time = time_seconds*FPS
ss = Params.ss  # screen size
N = Params.N
v = Params.v  # velocity
gridnum = Params.gridnum
seed = Params.seed
############################### MAIN ##############################################

### Load Configs

robots = Robots(N, v, ss, gridnum, seed)

group_list = [np.zeros(robots.num)]

### Simulation Loop

for t in range(sim_time):

    for r in range(robots.num):
        c = robots.coords[r].copy() # save previous position in case of collision
        # update robot positions
        robots.update_movement(r)

        # returns true if there was a collision
        # and moves robot back to original position and reorients


    sim_data.append([robots.coords[:,0].copy(), robots.coords[:,1].copy()])


data = pd.DataFrame(data = sim_data, columns = ["x","y"])

outdat = os.path.join(datadir, "demo.csv")

data.to_csv(outdat, lineterminator = "")

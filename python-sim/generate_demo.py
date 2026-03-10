import numpy as np
import pandas as pd
import os
import sys

# custom imports
from robots import Robots
from params import Params
from demo_parser import parse_args


########################## PARAMETERS ###########################################

#variables for saving data
sim_data = []
datadir = './data'
if not os.path.exists(datadir):
    os.mkdir(datadir)

#parse arguments
args = parse_args(sys.argv)

#assign variables from arguments
FPS = args.FPS
time_seconds = args.time_seconds
sim_time = time_seconds*FPS 
gridnum = args.time_seconds
ss = args.cell_size * gridnum 
N = args.N
v = args.v
seed = args.seed
strategy = args.strategy

############################### MAIN ##############################################

### Load Configs

robots = Robots(N, v, ss, gridnum, seed)

group_list = [np.zeros(robots.num)]

### Simulation Loop

for t in range(sim_time):

    for r in range(robots.num):
        c = robots.coords[r].copy() # save previous position in case of collision
        # update robot positions
        robots.plinko_movement_policy(r)

        # returns true if there was a collision
        # and moves robot back to original position and reorients


    sim_data.append([robots.coords[:,0].copy(), robots.coords[:,1].copy()])


data = pd.DataFrame(data = sim_data, columns = ["x","y"])

outdat = os.path.join(datadir, "demo.csv")

data.to_csv(outdat, lineterminator = "")

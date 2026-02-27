import numpy as np
import pandas as pd
import os
import sys

# custom imports
from robots import Robots
from params import Params


########################## PARAMETERS ###########################################

#variables for saving data
sim_data = []
datadir = './data'
if not os.path.exists(datadir):
    os.mkdir(datadir)

args = sys.argv[1:]
args = list(map(lambda x: x.split("="), args))
print(args)

arg_dict = {
    "FPS" : Params.FPS,
    "time_seconds" : Params.time_seconds,
    "ss" : Params.ss,  # screen size 
    "N" : Params.N, #num drones
    "v" : Params.v,  # velocity 
    "gridnum" : Params.gridnum,
    "seed" : Params.seed 
}

#for each arg passed, overwrite the default
for arg in args:
    if (arg[0] in arg_dict.keys()):
        #print("got here with" + arg[0])
        arg_dict[arg[0]] = int(arg[1])
        #print("now " + arg[0] + " = " + str(arg_dict[arg[0]]))

print(arg_dict["FPS"])
FPS = arg_dict["FPS"] 
time_seconds = arg_dict["time_seconds"]
sim_time = time_seconds*FPS
gridnum = arg_dict["gridnum"]
ss = Params.cell_size * gridnum 
N = arg_dict["N"]
v = arg_dict["v"]
seed = arg_dict["seed"]

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

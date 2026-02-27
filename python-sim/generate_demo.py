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
sim_time = Params.sim_time
ss = Params.ss  # screen size
N = Params.N
v = Params.v  # velocity
gridnum = Params.gridnum
seed = Params.seed

startLine = Params.startLine
finishLine = Params.finishLine


droneEntryTimes = {} # Create a dictionary to store drone's entry times.
                     # That way we can store drone's entry & exit times on one line.

############################### MAIN ##############################################

### Load Configs

robots = Robots(N, v, ss, gridnum, seed, startLine, finishLine)

group_list = [np.zeros(robots.num)]

### Simulation Loop

for t in range(sim_time):
    robots.update_movement()
    # We're already recording robot positions inside sim_data. Also, c was deleted.


    sim_data.append([robots.coords[:,0].copy(), robots.coords[:,1].copy()])

data = pd.DataFrame(data = sim_data, columns = ["x","y"])

outdat = os.path.join(datadir, "demo.csv")

data.to_csv(outdat, lineterminator = "")

robots.export_data()

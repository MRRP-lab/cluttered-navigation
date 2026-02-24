import numpy as np
import pandas as pd
import os

# custom imports
from robots import Robots
from params import Params
from data_logger import DataLogger

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

# TODO: Change filepath based on params
logger = DataLogger("EXAMPLE_FILEPATH")
############################### MAIN ##############################################

### Load Configs

robots = Robots(N, v, ss, gridnum, seed, startLine, finishLine)

group_list = [np.zeros(robots.num)]

### Simulation Loop

for t in range(sim_time):
    robots.update_movement()
    # We're already recording robot positions inside sim_data. Also, c was deleted.
    #logger.log_line(r, t, c[0], c[1])

    sim_data.append([robots.coords[:,0].copy(), robots.coords[:,1].copy()])
    logger.export_data()


data = pd.DataFrame(data = sim_data, columns = ["x","y"])

outdat = os.path.join(datadir, "demo.csv")

data.to_csv(outdat, lineterminator = "")

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

start_line = Params.startLine
finish_line = Params.finishLine

strategy = Params.strategy
reflectingBoundaryAngle = Params.reflectingBoundaryAngle

# Loggers:
logger_sp = DataLogger("Spatial", strategy, reflectingBoundaryAngle, N)
logger_ms = DataLogger("Makespan", strategy, reflectingBoundaryAngle, N)

drone_entry_times = {} # Create a dictionary to store drone's entry times.
                     # That way we can store drone's entry & exit times on one line.

############################### MAIN ##############################################

### Load Configs

robots = Robots(N, v, ss, gridnum, seed, start_line, finish_line)

group_list = [np.zeros(robots.num)]

### Simulation Loop

for t in range(sim_time):
    robots.update_movement()

    sim_data.append([robots.coords[:,0].copy(), robots.coords[:,1].copy()])
    
    # not ideal to do low-level logic in high level logic like this.
    # better to handle the logic inside a handler within the logger after passing it all the
    # relevant robot data.
    for r in range(len(robots.coords)):
        x = robots.coords[r,0]
        y = robots.coords[r,1]
        logger_sp.log_spatial(r, t, x, y)

        if x == start_line:
            drone_entry_times.update({r: t})
        elif x == finish_line:
            entryTime = drone_entry_times.get(r, -1) # Return negative 1 if the drone
            exitTime = t                           # did not cross the start line.
            logger_ms.log_makespan(r, entryTime, exitTime)

data = pd.DataFrame(data = sim_data, columns = ["x","y"])

outdat = os.path.join(datadir, "demo.csv")

data.to_csv(outdat, lineterminator = "")

logger_sp.export_data()
logger_ms.export_data()

